from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.constants import DEPARTMENTS, JOB_LEVELS, COUNTRIES

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=schemas.AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db)):
    return crud.get_analytics_summary(db)


@router.get("/reference-data")
def reference_data():
    """Static lookup lists the frontend uses to populate filters/dropdowns."""
    return {
        "departments": DEPARTMENTS,
        "job_levels": JOB_LEVELS,
        "countries": [{"name": c, "currency": v[0]} for c, v in COUNTRIES.items()],
    }
