"""
Pydantic schemas used for request bodies and API responses.
"""
import datetime as dt
from pydantic import BaseModel, EmailStr, Field


# ---------------- Auth / Users ----------------

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6)
    monthly_income: float = Field(0.0, ge=0)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    monthly_income: float

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------- Loans ----------------

class LoanCreate(BaseModel):
    lender_name: str = Field(..., min_length=2, max_length=120)
    loan_type: str = "Personal Loan"
    outstanding_amount: float = Field(..., gt=0)
    emi_amount: float = Field(..., ge=0)
    overdue_months: int = Field(0, ge=0)
    interest_rate: float = Field(0.0, ge=0)


class LoanOut(BaseModel):
    id: int
    lender_name: str
    loan_type: str
    outstanding_amount: float
    emi_amount: float
    overdue_months: int
    interest_rate: float
    created_at: dt.datetime

    class Config:
        from_attributes = True


# ---------------- Financial analysis / settlement ----------------

class FinancialHealthOut(BaseModel):
    monthly_income: float
    total_emi: float
    monthly_surplus: float
    emi_ratio: float
    debt_stress_score: float
    debt_stress_label: str
    total_outstanding: float
    average_overdue_months: float


class SettlementRequest(BaseModel):
    loan_id: int


class SettlementOut(BaseModel):
    id: int
    loan_id: int
    monthly_surplus: float
    emi_ratio: float
    debt_stress_score: float
    debt_stress_label: str
    suggested_settlement_pct: float
    suggested_settlement_amount: float
    ai_summary: str
    created_at: dt.datetime

    class Config:
        from_attributes = True


# ---------------- Negotiation letters ----------------

class NegotiationRequest(BaseModel):
    loan_id: int
    letter_type: str = Field("settlement_request", pattern="^(settlement_request|hardship_email|payment_plan_request)$")
    tone: str = Field("professional", pattern="^(professional|firm|empathetic)$")
    additional_context: str | None = None


class NegotiationOut(BaseModel):
    id: int
    loan_id: int
    letter_type: str
    generated_text: str
    created_at: dt.datetime

    class Config:
        from_attributes = True
