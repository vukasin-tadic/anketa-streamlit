import streamlit as st
import pandas as pd
from itertools import combinations
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ---------- 1. POMOĆNE FUNKCIJE ---------- #

def init_state():
    """Postavi session_state na početne vrednosti."""
    st.session_state["page"] = "entry"
    st.session_state["terms"] = []
    st.session_state["pairs"] = []
    st.session_state["idx"] = 0
    st.session_state["tally"] = {}

def start_survey():
    """Validiraj unete termine i pripremi parove."""
    terms = [t.strip() for t in st.session_state.term_inputs if t.strip()]
    if len(terms) != 5:
        st.warning("Popuni svih pet termina pre nego što nastaviš.")
        return

    st.session_state["terms"] = terms
    st.session_state["pairs"] = list(combinations(terms, 2))
    st.session_state["tally"] = {t: 0 for t in terms}
    st.session_state["idx"] = 0
    st.session_state["page"] = "survey"

def record_answer():
    """Upiši izbor i pređi na sledeće pitanje ili rezultate."""
    choice = st.session_state.get("choice")
    if not choice:
        st.warning("Izaberi jednu opciju pre nego što nastaviš.")
        return

    st.session_state["tally"][choice] += 1
    st.session_state["idx"] += 1

    if st.session_state["idx"] >= len(st.session_state["pairs"]):
        st.session_state["page"] = "results"
        save_to_sheet()
    else:
        # Obrisi izbor za sledeći radio
        st.session_state["choice"] = None

def save_to_sheet():
    """Upiši rezultate u Google Sheet (ignoriši grešku ako nema konekcije)."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = pd.DataFrame({
            "timestamp": [datetime.utcnow().isoformat(timespec="seconds")],
            **st.session_state["tally"]
        })
        conn.append(df, worksheet="responses", usecols=df.columns.tolist())
    except Exception as e:
        st.info(f"(Info) Podaci NISU upisani u Google Sheet: {e}")

# ---------- 2. GLAVNI TOK ---------- #

if "page" not in st.session_state:
    init_state()

st.title("Par-po-par anketa")

page = st.session_state["page"]

# --- Stranica 1: unos termina --- #
if page == "entry":
    st.subheader("Unesi pet termina po kojima želiš da odmeriš prioritete")
    st.session_state.term_inputs = [
        st.text_input(f"Termin {i+1}", key=f"term_{i}") for i in range(5)
    ]

    if st.button("Dalje ▶️", on_click=start_survey):
        pass  # logiku radi on_click

# --- Stranica 2: pitanja jedno po jedno --- #
elif page == "survey":
    pair = st.session_state["pairs"][st.session_state["idx"]]
    a, b = pair

    st.subheader(f"Pitanje {st.session_state['idx']+1} / {len(st.session_state['pairs'])}")
    st.radio(
        f"Šta ti je važnije?",
        options=pair,
        key="choice",
        horizontal=True
    )

    st.button("Sledeće ▶️", on_click=record_answer)

# --- Stranica 3: rezultati --- #
elif page == "results":
    st.success("Hvala! Evo kratke analize tvoje ankete:")

    tally = st.session_state["tally"]
    result_df = pd.DataFrame(
        {"Termin": tally.keys(), "Broj izbora": tally.values()}
    ).sort_values("Broj izbora", ascending=False)

    st.bar_chart(result_df.set_index("Termin"))

    st.write(result_df)

    if st.button("Pokreni novu anketu 🔄"):
        init_state()
