"""
SQLAlchemy ORM models.

User               -> registered borrower accounts
Loan               -> a borrower's individual loan/debt accounts
SettlementRecord   -> AI-generated settlement/financial-health snapshots for a loan
NegotiationHistory -> AI-generated negotiation letters/emails for a loan
"""
import datetime as dt

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    monthly_income = Column(Float, default=0.0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    loans = relationship("Loan", back_populates="owner", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    lender_name = Column(String(120), nullable=False)
    loan_type = Column(String(60), default="Personal Loan")
    outstanding_amount = Column(Float, nullable=False)
    emi_amount = Column(Float, nullable=False)
    overdue_months = Column(Integer, default=0)
    interest_rate = Column(Float, default=0.0)

    created_at = Column(DateTime, default=dt.datetime.utcnow)

    owner = relationship("User", back_populates="loans")
    settlements = relationship("SettlementRecord", back_populates="loan", cascade="all, delete-orphan")
    negotiations = relationship("NegotiationHistory", back_populates="loan", cascade="all, delete-orphan")


class SettlementRecord(Base):
    __tablename__ = "settlement_records"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)

    monthly_surplus = Column(Float)
    emi_ratio = Column(Float)
    debt_stress_score = Column(Float)
    debt_stress_label = Column(String(30))
    suggested_settlement_pct = Column(Float)
    suggested_settlement_amount = Column(Float)
    ai_summary = Column(Text)

    created_at = Column(DateTime, default=dt.datetime.utcnow)

    loan = relationship("Loan", back_populates="settlements")


class NegotiationHistory(Base):
    __tablename__ = "negotiation_history"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)

    letter_type = Column(String(40), default="settlement_request")
    generated_text = Column(Text)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    loan = relationship("Loan", back_populates="negotiations")
