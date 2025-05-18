# Pairwise Survey – Streamlit + Google Sheets

Collect pair‑wise preference data from users via a one‑page Streamlit app, store every response row in a Google Sheet, and give participants an immediate visual summary.

---

## ✨ Features

* **Custom terms** – participant supplies any 5 items.
* **Pair‑wise questions** – all 10 combinations, one click per screen.
* **Mandatory e‑mail** – simple regex validation.
* **Instant analytics** – bar‑chart & table after last answer.
* **Google Sheets logging** – timestamp, e‑mail, and per‑term counts.
* **Zero‑ops deploy** – GitHub → Streamlit Community Cloud auto‑build.

---

## 📂 Repository Layout

```
anketa-streamlit/
├─ app.py              # single‑file Streamlit app
├─ requirements.txt    # pinned deps (Streamlit, gspread, pandas …)
└─ .streamlit/
   ├─ config.toml       # optional Streamlit config (theme, etc.)
   └─ secrets.toml      # local secrets (NOT committed)
```

---

## 🔧 Prerequisites

1. **Google Cloud project** with *Sheets* & *Drive* APIs enabled.
2. **Service account** JSON key   → share target spreadsheet (**Editor**).
3. **Streamlit Cloud** account (GitHub login).
4. Python ≥ 3.9 if you run locally.

---

## 🚀 Quick Start (Local)

```bash
# clone
$ git clone https://github.com/<you>/anketa-streamlit.git && cd anketa-streamlit

# create venv (optional)
$ python -m venv .venv && source .venv/bin/activate

# install deps
$ pip install -r requirements.txt

# add secrets
$ mkdir -p .streamlit && nano .streamlit/secrets.toml
```

`secrets.toml` example:

```toml
spreadsheet_id = "<SPREADSHEET_ID>"

[gsheets_service_account]
# … full JSON key here …
```

Run:

```bash
$ streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push repo to GitHub.
2. *streamlit.io/cloud* → **Create app** → pick repo & branch.
3. Paste **the same secrets** into *Settings ▶ Edit secrets*.
4. Click **Deploy** – first build ≈ 1 min.
5. Each `git push` auto‑redeploys.

---

## 🗃️ Data Schema (`responses` worksheet)

| Column                  | Example                                     |
| ----------------------- | ------------------------------------------- |
| `timestamp`             | 2025‑05‑18T09:30:12Z                        |
| `email`                 | [user@example.com](mailto:user@example.com) |
| `termin 1` … `termin 5` | `jabuka, 4` (name, count)                   |

Counts = number of pair‑wise wins per term.

---

## 📈 Analytics Ideas

* Import sheet to Looker Studio or DataFrame: `pd.read_csv(export_url)`
* Fit Bradley‑Terry or Elo model on pair‑wise wins.
* Track time‑stamped trends per term.

---

## 🤝 Contributing

1. Fork ➜ feature branch ➜ PR.
2. Run `black app.py` before committing.
3. All changes auto‑deployed to staging app (`dev` branch).

---


