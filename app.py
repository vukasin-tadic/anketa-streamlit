import streamlit as st
import pandas as pd
from datetime import datetime
from itertools import combinations
import re

import gspread
from google.oauth2 import service_account

# ---------- 1.  G-Sheets konekcija ---------- #
@st.cache_resource
def get_worksheet():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gsheets_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(st.secrets["spreadsheet_id"])

    # worksheet „responses“ kreiramo ako ne postoji
    try:
        ws = sh.worksheet("responses")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title="responses", rows=1, cols=20)

    # zaglavlje (radi samo prvi put)
    if ws.row_count == 0 or ws.cell(1, 1).value is None:
        ws.append_row(
            [
                "timestamp",
                "email",
                "termin 1",
                "termin 2",
                "termin 3",
                "termin 4",
                "termin 5",
            ]
        )
    return ws


ws = get_worksheet()


def save_to_sheet(email: str, terms: list[str], tally: dict[str, int]):
    row = [
        datetime.utcnow().isoformat(timespec="seconds"),
        email,
    ]
    # zadržavamo isti redosled kao pri unosu
    for t in terms:
        row.append(f"{t}, {tally[t]}")
    ws.append_row(row, value_input_option="RAW")


# ---------- 2.  Streamlit logika ---------- #
def init_state():
    st.session_state.page = "entry"
    st.session_state.email = ""
    st.session_state.term_inputs = [""] * 5
    st.session_state.terms = []
    st.session_state.pairs = []
    st.session_state.idx = 0
    st.session_state.tally = {}


def valid_email(e: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", e or "") is not None


def start_survey():
    email = st.session_state.email.strip()
    if not valid_email(email):
        st.warning("Unesi **ispravan e-mail** (obavezan).")
        return

    terms = [t.strip() for t in st.session_state.term_inputs if t.strip()]
    if len(terms) != 5:
        st.warning("Popuni **svih pet** termina.")
        return

    st.session_state.terms = terms
    st.session_state.tally = {t: 0 for t in terms}
    st.session_state.pairs = list(combinations(terms, 2))
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
        save_to_sheet(
            st.session_state.email, st.session_state.terms, st.session_state.tally
        )
        st.session_state.page = "results"
    else:
        st.session_state.choice = None  # reset radio


# -------------- MAIN -------------- #
if "page" not in st.session_state:
    init_state()

st.title("Par-po-par anketa")

if st.session_state.page == "entry":
    st.subheader("1) Osnovni podaci")

    st.session_state.email = st.text_input(
        "Tvoj e-mail (obavezno)", value=st.session_state.email, key="email_input"
    )

    st.divider()
    st.subheader("2) Unesi pet termina")

    for i in range(5):
        st.session_state.term_inputs[i] = st.text_input(
            f"Termin {i+1}", value=st.session_state.term_inputs[i], key=f"term_{i}"
        )

    st.button("Dalje ▶️", on_click=start_survey)

elif st.session_state.page == "survey":
    a, b = st.session_state.pairs[st.session_state.idx]
    st.subheader(
        f"Pitanje {st.session_state.idx + 1} / {len(st.session_state.pairs)}"
    )
    st.radio("Šta ti je važnije?", (a, b), key="choice", horizontal=True)
    st.button("Sledeće ▶️", on_click=record_answer)

elif st.session_state.page == "results":
    st.success("Hvala! Rezime tvojih izbora:")
    df = (
        pd.DataFrame(
            {
                "Termin": st.session_state.terms,
                "Broj izbora": [st.session_state.tally[t] for t in st.session_state.terms],
            }
        )
        .sort_values("Broj izbora", ascending=False)
        .reset_index(drop=True)
    )

    st.bar_chart(df.set_index("Termin"))
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.button("Nova anketa 🔄", on_click=init_state)
