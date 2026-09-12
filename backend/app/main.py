import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import employees, analytics

# Create tables on startup if they don't exist yet. For a v1 SQLite-backed system
# of record this is sufficient; a real deployment would use Alembic migrations
# (noted in docs/ARCHITECTURE.md).
Base.metadata.create_all(bind=engine)


def _seed_if_empty() -> None:
    # Populate a demo dataset when the database is empty.
    #
    # Why this exists: on a serverless host (e.g. Vercel) the filesystem is
    # ephemeral, so a SQLite file seeded at build time is gone by the time a
    # request arrives -- the API then correctly returns zero employees and the UI
    # looks broken. Re-seeding on startup whenever the table is empty makes that
    # environment self-healing and demo-able.
    #
    # Safe by construction: it only runs when there are zero employees, so it
    # never clobbers real data. Set SEED_ON_STARTUP=0 to disable, or
    # SEED_ON_STARTUP_COUNT to change the demo size.
    if os.environ.get("SEED_ON_STARTUP", "1") != "1":
        return

    try:
        from app.models import Employee
        from app.database import SessionLocal
        from seed import seed

        db = SessionLocal()
        try:
            empty = db.query(Employee).count() == 0
        finally:
            db.close()

        if empty:
            count = int(os.environ.get("SEED_ON_STARTUP_COUNT", "10000"))
            seed(count=count, reset=False)
    except Exception as exc:  # pragma: no cover - startup must never hard-fail
        # A failed seed should not take the whole API down; the health check and
        # every read endpoint still work, and the cause is visible in the logs.
        print(f"[startup] demo seed skipped: {exc}")


_seed_if_empty()


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
