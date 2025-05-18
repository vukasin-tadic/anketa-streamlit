import streamlit as st
import pandas as pd
from datetime import datetime
from itertools import combinations
#
import gspread
from google.oauth2 import service_account

# -------------------------------------------------
# 1.  G-Sheets konekcija (koristi service-account JSON iz secrets.toml)
# -------------------------------------------------
@st.cache_resource
def get_worksheet():
    # ❶ ceo JSON ključ je u pod-sekciji [gsheets_service_account]
    creds_dict = st.secrets["gsheets_service_account"]
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    gc = gspread.authorize(creds)

    # ❷ spreadsheet_id je na korenu secrets-a
    sh = gc.open_by_key(st.secrets["spreadsheet_id"])

    try:
        return sh.worksheet("responses")
    except gspread.WorksheetNotFound:
        return sh.add_worksheet(title="responses", rows=1, cols=20)


ws = get_worksheet()  # globalni handle: gspread.worksheet.Worksheet


def save_to_sheet(tally: dict[str, int]) -> None:
    """Upiši jedan red (timestamp + rezultati) u tablicu."""
    row = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        **tally,
    }
    ws.append_rows([list(row.values())])


# -------------------------------------------------
# 2.  Streamlit UI logika (3 ekrana u session_state)
# -------------------------------------------------
def init_state():
    st.session_state.page = "entry"
    st.session_state.term_inputs = [""] * 5
    st.session_state.terms = []
    st.session_state.pairs = []
    st.session_state.idx = 0
    st.session_state.tally = {}


def start_survey():
    terms = [t.strip() for t in st.session_state.term_inputs if t.strip()]
    if len(terms) != 5:
        st.warning("Popuni **svih pet** termina.")
        return

    st.session_state.terms = terms
    st.session_state.pairs = list(combinations(terms, 2))
    st.session_state.tally = {t: 0 for t in terms}
    st.session_state.idx = 0
    st.session_state.page = "survey"


def record_answer():
    choice = st.session_state.get("choice")
    if not choice:
        st.warning("Izaberi opciju pa klikni *Sledeće*.")
        return

    st.session_state.tally[choice] += 1
    st.session_state.idx += 1

    if st.session_state.idx >= len(st.session_state.pairs):
        save_to_sheet(st.session_state.tally)
        st.session_state.page = "results"
    else:
        st.session_state.choice = None  # reset radio


# ===============  MAIN  =================
if "page" not in st.session_state:
    init_state()

st.title("Par-po-par anketa")

page = st.session_state.page

# --- 1) Unos termina --- #
if page == "entry":
    st.subheader("Unesi pet termina")
    for i in range(5):
        st.session_state.term_inputs[i] = st.text_input(
            f"Termin {i + 1}", value=st.session_state.term_inputs[i], key=f"term_{i}"
        )

    st.button("Dalje ▶️", on_click=start_survey)

# --- 2) Pitanja --- #
elif page == "survey":
    a, b = st.session_state.pairs[st.session_state.idx]
    st.subheader(
        f"Pitanje {st.session_state.idx + 1} / {len(st.session_state.pairs)}"
    )
    st.radio(
        "Šta ti je važnije?",
        (a, b),
        key="choice",
        horizontal=True,
    )
    st.button("Sledeće ▶️", on_click=record_answer)

# --- 3) Rezultati --- #
elif page == "results":
    st.success("Hvala na popunjavanju! 👇 Evo rezultata:")
    tally = st.session_state.tally
    df = (
        pd.DataFrame({"Termin": tally.keys(), "Broj izbora": tally.values()})
        .sort_values("Broj izbora", ascending=False)
        .reset_index(drop=True)
    )

    st.bar_chart(df.set_index("Termin"))
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.button("Pokreni novu anketu 🔄", on_click=init_state)
