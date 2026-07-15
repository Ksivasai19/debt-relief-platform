# AI Powered Debt Relief & Financial Recovery Platform

An AI-driven web application that helps borrowers manage debt, analyze financial
health, and generate settlement/negotiation strategies.

**Stack:** React.js (Vite) · FastAPI · Python · SQLite · SQLAlchemy ORM · Google Gemini API

---

## What's included

- **Auth** — register/login with JWT tokens, hashed passwords (bcrypt)
- **Loan management** — add, edit, delete loan accounts (lender, outstanding amount, EMI, overdue months, interest rate)
- **Financial health dashboard** — monthly surplus, EMI-to-income ratio, a 0–100 debt stress score/label, total outstanding
- **AI-powered settlement predictor** (Scenario 1) — rule-based settlement-percentage engine + Gemini-generated plain-English summary
- **AI negotiation letter generator** (Scenario 2) — Gemini-generated settlement/hardship/payment-plan letters, tailored to lender and tone
- **Negotiation & settlement history** — every AI-generated letter and settlement analysis is stored per loan

> Note: the settlement percentage itself is computed with a transparent, rule-based
> formula (see `backend/app/financial_engine.py`) rather than asked directly of the
> LLM — this keeps the numbers consistent and explainable. Gemini is then used to
> turn those numbers into natural-language insights and letters.

---

## 1. Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- A free Google Gemini API key: https://aistudio.google.com/app/apikey
  (the app also works without a key — see "Running without a Gemini key" below)

---

## 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # Windows: copy .env.example .env
# then open .env and paste your GEMINI_API_KEY, and set a real JWT_SECRET_KEY

uvicorn app.main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`.
Interactive API docs (Swagger UI): `http://localhost:8000/docs`

A `debt_relief.db` SQLite file is created automatically on first run — no manual
migration step needed for this prototype.

---

## 3. Frontend setup

Open a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

The app will be live at `http://localhost:5173` and will proxy `/api/*` calls
to the backend at `http://localhost:8000` (see `vite.config.js`).

---

## 4. Using the app

1. Go to `http://localhost:5173`, click **Create one**, register with your name,
   email, password, and monthly income.
2. Go to **Loans** and add one or more loan accounts (lender, outstanding amount,
   EMI, months overdue, interest rate).
3. Check the **Dashboard** for your financial health summary.
4. Go to **Settlement Predictor**, pick a loan, and click **Predict Settlement**
   for an AI-analyzed settlement percentage + summary.
5. Go to **AI Letter Generator**, pick a loan and letter type/tone, and generate
   a ready-to-send negotiation letter.

---

## 5. Running without a Gemini key

If `GEMINI_API_KEY` is left blank in `.env`, the settlement summary and letter
generator automatically fall back to clearly-labelled template text instead of
calling the AI — so you can develop, demo, and test the whole app end-to-end
before you obtain a key.

---

## 6. Project structure

```
backend/
  app/
    main.py            FastAPI app, CORS, router wiring
    config.py           Settings loaded from .env
    database.py          SQLAlchemy engine/session
    models.py             User, Loan, SettlementRecord, NegotiationHistory
    schemas.py             Pydantic request/response models
    auth.py                  Password hashing + JWT
    financial_engine.py       EMI ratio / debt-stress / settlement % logic
    ai_service.py               Gemini integration (with offline fallback)
    routers/
      auth.py, loans.py, financial.py, settlement.py, negotiation.py
  requirements.txt
  .env.example

frontend/
  src/
    api/client.js           Axios instance with JWT interceptor
    context/AuthContext.jsx  Login/register/logout state
    components/Layout.jsx    Sidebar + page shell
    pages/
      Login.jsx, Register.jsx, Dashboard.jsx, Loans.jsx,
      SettlementPredictor.jsx, LetterGenerator.jsx
  package.json
  vite.config.js
```

---

## 7. API reference (once running)

Full interactive docs at `/docs`. Key endpoints:

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account, returns JWT |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user info |
| GET/POST | `/api/loans` | List / create loans |
| PUT/DELETE | `/api/loans/{id}` | Update / delete a loan |
| GET | `/api/financial/health` | Aggregate financial health metrics |
| POST | `/api/settlement/predict` | AI settlement recommendation |
| GET | `/api/settlement/history/{loan_id}` | Past settlement analyses |
| POST | `/api/negotiation/generate-letter` | AI negotiation letter |
| GET | `/api/negotiation/history/{loan_id}` | Past generated letters |

---

## 8. Disclaimer

This tool provides automated, rule-based estimates and AI-generated drafts to
help borrowers *start* a conversation with lenders. It is **not** financial or
legal advice, and settlement outcomes are never guaranteed. Always verify with
your lender and a qualified financial/legal advisor before acting.
