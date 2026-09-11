from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import employees, analytics

# Create tables on startup if they don't exist yet. For a v1 SQLite-backed system
# of record this is sufficient; a real deployment would use Alembic migrations
# (noted in docs/ARCHITECTURE.md).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ACME Salary Management API",
    description="API for managing employee salary data across ACME's global org.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # single-tenant internal tool for this exercise
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(analytics.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
