import datetime as dt
import statistics
from typing import Optional, Tuple, List

from sqlalchemy import func, and_
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.constants import COUNTRIES, LEVEL_MULTIPLIER


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

def _next_employee_code(db: Session) -> str:
    last = db.query(func.max(models.Employee.id)).scalar() or 0
    return f"EMP-{last + 1:06d}"


def create_employee(db: Session, payload: schemas.EmployeeCreate) -> models.Employee:
    currency = payload.starting_salary.currency
    employee = models.Employee(
        employee_code=_next_employee_code(db),
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        department=payload.department,
        job_title=payload.job_title,
        job_level=payload.job_level,
        country=payload.country,
        currency=currency,
        manager_id=payload.manager_id,
        status=payload.status or "active",
        hire_date=payload.hire_date,
    )
    db.add(employee)
    db.flush()  # populate employee.id without committing yet

    salary = models.SalaryRecord(
        employee_id=employee.id,
        base_salary=payload.starting_salary.base_salary,
        currency=currency,
        bonus_target_pct=payload.starting_salary.bonus_target_pct,
        effective_date=payload.starting_salary.effective_date,
        reason=payload.starting_salary.reason or "Initial hire",
    )
    db.add(salary)
    db.commit()
    db.refresh(employee)
    return employee


def get_employee(db: Session, employee_id: int) -> Optional[models.Employee]:
    return (
        db.query(models.Employee)
        .options(joinedload(models.Employee.salary_records))
        .filter(models.Employee.id == employee_id)
        .first()
    )


def update_employee(
    db: Session, employee: models.Employee, payload: schemas.EmployeeUpdate
) -> models.Employee:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


def deactivate_employee(db: Session, employee: models.Employee) -> models.Employee:
    employee.status = "inactive"
    db.commit()
    db.refresh(employee)
    return employee


def add_salary_record(
    db: Session, employee: models.Employee, payload: schemas.SalaryRecordCreate
) -> models.SalaryRecord:
    record = models.SalaryRecord(
        employee_id=employee.id,
        base_salary=payload.base_salary,
        currency=payload.currency,
        bonus_target_pct=payload.bonus_target_pct,
        effective_date=payload.effective_date,
        reason=payload.reason,
    )
    db.add(record)
    # Keep the employee's denormalized "current currency" in sync in case a
    # relocation changes pay currency.
    employee.currency = payload.currency
    db.commit()
    db.refresh(record)
    return record


def current_salary_subquery(db: Session):
    """
    Correlated subquery returning each employee's most recent salary_records.id
    (by effective_date, tie-broken by id) — i.e. their *current* salary row.
    Used everywhere we need "current salary" without loading full history.
    """
    sr = models.SalaryRecord
    latest = (
        db.query(
            sr.employee_id.label("employee_id"),
            func.max(sr.effective_date).label("max_date"),
        )
        .group_by(sr.employee_id)
        .subquery()
    )
    return latest


def list_employees(
    db: Session,
    page: int = 1,
    page_size: int = 25,
    department: Optional[str] = None,
    country: Optional[str] = None,
    job_level: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """
    Server-side filtered/paginated employee list with each row's *current*
    salary, computed via a single joined query (no N+1) so this stays fast
    at 10k+ rows.
    """
    sr = models.SalaryRecord
    emp = models.Employee

    latest_dates = current_salary_subquery(db)

    current_salary = (
        db.query(sr.employee_id, sr.base_salary, sr.currency)
        .join(
            latest_dates,
            and_(
                sr.employee_id == latest_dates.c.employee_id,
                sr.effective_date == latest_dates.c.max_date,
            ),
        )
        .subquery()
    )

    query = (
        db.query(
            emp,
            current_salary.c.base_salary,
            current_salary.c.currency,
        )
        .outerjoin(current_salary, current_salary.c.employee_id == emp.id)
    )

    if department:
        query = query.filter(emp.department == department)
    if country:
        query = query.filter(emp.country == country)
    if job_level:
        query = query.filter(emp.job_level == job_level)
    if status:
        query = query.filter(emp.status == status)
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            func.lower(emp.first_name + " " + emp.last_name).like(like)
            | func.lower(emp.email).like(like)
            | func.lower(emp.employee_code).like(like)
        )

    total = query.count()

    rows = (
        query.order_by(emp.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for employee, salary, currency in rows:
        items.append(
            {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email": employee.email,
                "department": employee.department,
                "job_title": employee.job_title,
                "job_level": employee.job_level,
                "country": employee.country,
                "status": employee.status,
                "current_salary": salary,
                "currency": currency,
            }
        )
    return items, total


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def _group_stats(rows: List[Tuple[str, float, str]]) -> List[schemas.GroupAverage]:
    """rows: list of (group_key, salary, currency) -> aggregated stats per group."""
    buckets: dict[str, list] = {}
    currency_by_group: dict[str, str] = {}
    for group, salary, currency in rows:
        buckets.setdefault(group, []).append(salary)
        currency_by_group[group] = currency

    result = []
    for group, values in sorted(buckets.items()):
        result.append(
            schemas.GroupAverage(
                group=group,
                headcount=len(values),
                avg_salary=round(statistics.mean(values), 2),
                median_salary=round(statistics.median(values), 2),
                total_cost=round(sum(values), 2),
                currency=currency_by_group[group],
            )
        )
    return result


def get_analytics_summary(db: Session) -> schemas.AnalyticsSummary:
    emp = models.Employee
    sr = models.SalaryRecord

    total_employees = db.query(func.count(emp.id)).scalar() or 0
    active_employees = (
        db.query(func.count(emp.id)).filter(emp.status == "active").scalar() or 0
    )
    inactive_employees = total_employees - active_employees

    latest_dates = current_salary_subquery(db)
    current_rows = (
        db.query(emp.department, emp.country, emp.job_level, sr.base_salary, sr.currency)
        .join(sr, sr.employee_id == emp.id)
        .join(
            latest_dates,
            and_(
                sr.employee_id == latest_dates.c.employee_id,
                sr.effective_date == latest_dates.c.max_date,
            ),
        )
        .filter(emp.status == "active")
        .all()
    )

    by_department = _group_stats([(r[0], r[3], r[4]) for r in current_rows])
    by_country = _group_stats([(r[1], r[3], r[4]) for r in current_rows])
    by_level = _group_stats([(r[2], r[3], r[4]) for r in current_rows])

    # Pay index = salary / that country's L1 base salary (see schemas.py docstring).
    pay_indexes = []
    for _, country, _, salary, _ in current_rows:
        base = COUNTRIES.get(country, (None, None))[1]
        if base:
            pay_indexes.append(salary / base)

    histogram = _build_histogram(pay_indexes, num_buckets=10)

    return schemas.AnalyticsSummary(
        total_employees=total_employees,
        active_employees=active_employees,
        inactive_employees=inactive_employees,
        by_department=by_department,
        by_country=by_country,
        by_level=by_level,
        pay_index_histogram=histogram,
    )


def _build_histogram(values: List[float], num_buckets: int = 10) -> List[schemas.HistogramBucket]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        hi = lo + 1  # avoid a zero-width bucket for degenerate/tiny datasets
    width = (hi - lo) / num_buckets
    counts = [0] * num_buckets
    for v in values:
        idx = min(int((v - lo) / width), num_buckets - 1)
        counts[idx] += 1
    return [
        schemas.HistogramBucket(
            range_start=round(lo + i * width, 2),
            range_end=round(lo + (i + 1) * width, 2),
            count=counts[i],
        )
        for i in range(num_buckets)
    ]
