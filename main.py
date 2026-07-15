"""
AI Powered Debt Relief & Financial Recovery Platform - FastAPI entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, loans, financial, settlement, negotiation

# Create tables on startup (fine for SQLite + a student/prototype project;
# use Alembic migrations for anything production-grade).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Powered Debt Relief & Financial Recovery Platform",
    description="APIs for loan management, financial health analysis, "
                "AI-powered settlement recommendations, and negotiation letter generation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(loans.router)
app.include_router(financial.router)
app.include_router(settlement.router)
app.include_router(negotiation.router)


@app.get("/api/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "debt-relief-platform-api"}
