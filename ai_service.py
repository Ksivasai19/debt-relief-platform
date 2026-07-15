"""
Google Gemini integration for:
  1. Natural-language financial health / settlement summaries
  2. AI-generated negotiation letters and settlement request emails

If GEMINI_API_KEY is not set, each function falls back to a clearly-labelled
template response so the rest of the app remains fully testable without an
API key.
"""
import google.generativeai as genai

from app.config import settings

_model = None


def _get_model():
    global _model
    if not settings.GEMINI_API_KEY:
        return None
    if _model is None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-flash-latest")
    return _model


def generate_settlement_summary(*, lender_name: str, outstanding_amount: float,
                                 emi_amount: float, overdue_months: int,
                                 monthly_income: float, emi_ratio: float,
                                 debt_stress_label: str,
                                 suggested_settlement_pct: float) -> str:
    model = _get_model()
    prompt = f"""You are a calm, factual financial-wellness assistant helping a borrower
understand their situation. Do NOT give legal advice or guarantee outcomes.

Borrower data:
- Lender: {lender_name}
- Outstanding amount: {outstanding_amount}
- Monthly EMI: {emi_amount}
- Months overdue: {overdue_months}
- Monthly income: {monthly_income}
- EMI-to-income ratio: {emi_ratio}%
- Debt stress level: {debt_stress_label}
- Suggested opening settlement offer: {suggested_settlement_pct}% of outstanding amount

Write a short (100-140 word) plain-English summary of their financial health
regarding this loan and explain, in one short paragraph, the reasoning behind
the suggested settlement percentage. End with a one-sentence reminder that
this is a starting point for negotiation, not guaranteed or legal advice."""

    if model is None:
        return (
            f"[Offline template \u2014 no GEMINI_API_KEY configured]\n"
            f"With a {debt_stress_label.lower()} debt stress level and an EMI-to-income ratio of "
            f"{emi_ratio}%, this {lender_name} loan is placing meaningful pressure on your monthly "
            f"budget. Based on {overdue_months} month(s) overdue and your available surplus, a "
            f"starting settlement offer of around {suggested_settlement_pct}% of the outstanding "
            f"amount ({outstanding_amount}) is a reasonable opening position for negotiation. "
            f"Note: this is an automated starting estimate, not financial or legal advice \u2014 "
            f"please verify details with the lender and a qualified advisor before proceeding."
        )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:  # pragma: no cover - network/SDK errors
        return f"AI summary temporarily unavailable ({e}). Please try again shortly."


_LETTER_TYPE_LABELS = {
    "settlement_request": "a one-time settlement request",
    "hardship_email": "a financial hardship notification",
    "payment_plan_request": "a revised payment plan / restructuring request",
}

_TONE_LABELS = {
    "professional": "polite, professional, and businesslike",
    "firm": "firm and direct, while remaining respectful",
    "empathetic": "warm and empathetic, while remaining clear and professional",
}


def generate_negotiation_letter(*, lender_name: str, loan_type: str,
                                 outstanding_amount: float, emi_amount: float,
                                 overdue_months: int, monthly_income: float,
                                 suggested_settlement_pct: float,
                                 suggested_settlement_amount: float,
                                 letter_type: str, tone: str,
                                 additional_context: str | None) -> str:
    model = _get_model()
    letter_purpose = _LETTER_TYPE_LABELS.get(letter_type, "a settlement request")
    tone_desc = _TONE_LABELS.get(tone, "professional")

    prompt = f"""Write {letter_purpose} letter/email from a borrower to their lender.
Tone: {tone_desc}. Keep it under 250 words, properly formatted with a greeting,
body, and sign-off placeholder "[Your Name]". Do not invent legal claims or
threaten the lender. Reference these real facts naturally in the letter:

- Lender name: {lender_name}
- Loan type: {loan_type}
- Outstanding amount: {outstanding_amount}
- Monthly EMI: {emi_amount}
- Months overdue: {overdue_months}
- Monthly income: {monthly_income}
- Proposed settlement: {suggested_settlement_pct}% of outstanding, approximately {suggested_settlement_amount}
Additional context from borrower: {additional_context or "None provided"}
"""

    if model is None:
        return (
            f"[Offline template \u2014 no GEMINI_API_KEY configured]\n\n"
            f"Subject: Request Regarding {loan_type} Account \u2013 {lender_name}\n\n"
            f"Dear {lender_name} Team,\n\n"
            f"I am writing regarding my {loan_type.lower()} account with an outstanding balance of "
            f"{outstanding_amount}. Due to financial hardship, I have fallen behind by "
            f"{overdue_months} month(s) on my EMI of {emi_amount}.\n\n"
            f"I would like to propose a one-time settlement of approximately "
            f"{suggested_settlement_amount} ({suggested_settlement_pct}% of the outstanding amount), "
            f"which reflects my current repayment capacity based on a monthly income of "
            f"{monthly_income}. {additional_context or ''}\n\n"
            f"I would appreciate the opportunity to discuss this proposal at your earliest "
            f"convenience.\n\nSincerely,\n[Your Name]"
        )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:  # pragma: no cover
        return f"AI letter generation temporarily unavailable ({e}). Please try again shortly."
