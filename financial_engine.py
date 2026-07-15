"""
Rule-based financial analysis engine.

This provides deterministic, explainable calculations for:
  - monthly surplus / EMI ratio
  - a 0-100 debt stress score and label
  - a suggested settlement percentage

These numbers are then handed to the Gemini AI service (ai_service.py) to be
turned into a natural-language summary and negotiation letters. Keeping the
math rule-based (rather than asking the LLM to compute it) makes the figures
consistent, auditable, and safe to show to a user managing real debt.
"""
from dataclasses import dataclass


@dataclass
class FinancialHealth:
    monthly_income: float
    total_emi: float
    monthly_surplus: float
    emi_ratio: float          # total_emi / monthly_income, as a percentage
    debt_stress_score: float  # 0-100, higher = more stressed
    debt_stress_label: str    # Low / Moderate / High / Severe
    total_outstanding: float
    average_overdue_months: float


def compute_financial_health(monthly_income: float, loans: list) -> FinancialHealth:
    """loans: list of ORM Loan objects (or anything with the same attributes)."""
    total_emi = sum(l.emi_amount for l in loans) if loans else 0.0
    total_outstanding = sum(l.outstanding_amount for l in loans) if loans else 0.0
    avg_overdue = (sum(l.overdue_months for l in loans) / len(loans)) if loans else 0.0

    income = max(monthly_income, 1.0)  # avoid division by zero
    monthly_surplus = income - total_emi
    emi_ratio = round((total_emi / income) * 100, 2)

    # Debt stress score: weighted blend of EMI ratio, overdue months, and
    # outstanding-to-income multiple. Each component is capped so one extreme
    # value can't single-handedly max out the score.
    emi_component = min(emi_ratio, 100) * 0.5
    overdue_component = min(avg_overdue * 8, 100) * 0.3
    outstanding_multiple = total_outstanding / income if income else 0
    outstanding_component = min(outstanding_multiple * 10, 100) * 0.2
    debt_stress_score = round(emi_component + overdue_component + outstanding_component, 1)
    debt_stress_score = max(0.0, min(debt_stress_score, 100.0))

    if debt_stress_score < 30:
        label = "Low"
    elif debt_stress_score < 55:
        label = "Moderate"
    elif debt_stress_score < 80:
        label = "High"
    else:
        label = "Severe"

    return FinancialHealth(
        monthly_income=income,
        total_emi=round(total_emi, 2),
        monthly_surplus=round(monthly_surplus, 2),
        emi_ratio=emi_ratio,
        debt_stress_score=debt_stress_score,
        debt_stress_label=label,
        total_outstanding=round(total_outstanding, 2),
        average_overdue_months=round(avg_overdue, 1),
    )


def suggest_settlement_percentage(outstanding_amount: float, overdue_months: int,
                                   monthly_surplus: float) -> float:
    """
    Heuristic starting point for a settlement offer, expressed as a percentage
    of the outstanding amount. This is a starting negotiation anchor, not
    financial or legal advice, and should always be reviewed by the user.
    """
    base = 55.0  # start around slightly-above-half as a natural anchor

    # Longer overdue history typically increases a lender's willingness to
    # settle for less, since the debt is more likely to be written off.
    if overdue_months >= 12:
        base -= 20
    elif overdue_months >= 6:
        base -= 12
    elif overdue_months >= 3:
        base -= 6

    # A borrower with negative or very thin surplus has less real ability to
    # pay, which also supports a lower settlement figure.
    if monthly_surplus < 0:
        base -= 10
    elif monthly_surplus < outstanding_amount * 0.02:
        base -= 5

    return round(max(20.0, min(base, 85.0)), 1)
