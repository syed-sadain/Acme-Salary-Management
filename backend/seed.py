"""
Seed the database with 10,000 employees spread across countries/departments/levels,
each with an initial salary record and a plausible salary-history trail.

Salaries are NOT uniform random — they're built from a country base band x level
multiplier x small role/tenure noise, so the analytics dashboard shows a
realistic, explainable distribution instead of flat noise.

Usage:
    python seed.py            # seeds 10,000 employees (default)
    python seed.py --count 500 --reset
"""
import argparse
import datetime as dt
import random

from faker import Faker

from app.database import Base, engine, SessionLocal
from app.models import Employee, SalaryRecord
from app.constants import DEPARTMENTS, JOB_LEVELS, LEVEL_MULTIPLIER, COUNTRIES

fake = Faker()
Faker.seed(42)
random.seed(42)

# Departments skew realistically: most orgs are Engineering/Sales-heavy, not evenly split.
DEPARTMENT_WEIGHTS = [30, 20, 10, 8, 7, 12, 8, 5]  # matches order of DEPARTMENTS
LEVEL_WEIGHTS = [35, 30, 20, 10, 5]  # most employees are junior/mid, few principals
COUNTRY_WEIGHTS = [35, 25, 12, 10, 10, 8]  # matches order of COUNTRIES keys


def random_hire_date() -> dt.date:
    days_ago = random.randint(30, 365 * 12)
    return dt.date.today() - dt.timedelta(days=days_ago)


def salary_for(level: str, country: str) -> float:
    currency, base = COUNTRIES[country]
    multiplier = LEVEL_MULTIPLIER[level]
    noise = random.uniform(0.9, 1.15)  # +/- individual variance within a band
    return round(base * multiplier * noise, -2)  # round to nearest 100


def build_employee(idx: int) -> tuple[Employee, list[SalaryRecord]]:
    department = random.choices(DEPARTMENTS, weights=DEPARTMENT_WEIGHTS, k=1)[0]
    level = random.choices(JOB_LEVELS, weights=LEVEL_WEIGHTS, k=1)[0]
    country = random.choices(list(COUNTRIES.keys()), weights=COUNTRY_WEIGHTS, k=1)[0]
    currency = COUNTRIES[country][0]

    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name}.{last_name}{idx}@acme-corp.com".lower()

    hire_date = random_hire_date()
    status = "active" if random.random() > 0.04 else "inactive"  # ~4% attrition

    employee = Employee(
        employee_code=f"EMP-{idx:06d}",
        first_name=first_name,
        last_name=last_name,
        email=email,
        department=department,
        job_title=f"{level.split(' - ')[1]} {department.rstrip('s')}",
        job_level=level,
        country=country,
        currency=currency,
        status=status,
        hire_date=hire_date,
    )

    # Build 1-3 salary records: initial hire, and occasional raises since then.
    records = []
    tenure_years = max(0, (dt.date.today() - hire_date).days // 365)
    num_raises = min(tenure_years, random.choice([0, 0, 1, 1, 2]))

    current_date = hire_date
    current_salary = salary_for(level, country) * 0.85  # start a bit below current band
    records.append(
        SalaryRecord(
            base_salary=round(current_salary, -2),
            currency=currency,
            bonus_target_pct=round(random.uniform(0, 15), 1),
            effective_date=current_date,
            reason="Initial hire",
        )
    )

    for _ in range(num_raises):
        gap_days = random.randint(180, 500)
        current_date = current_date + dt.timedelta(days=gap_days)
        if current_date >= dt.date.today():
            break
        current_salary *= random.uniform(1.04, 1.12)
        records.append(
            SalaryRecord(
                base_salary=round(current_salary, -2),
                currency=currency,
                bonus_target_pct=round(random.uniform(0, 20), 1),
                effective_date=current_date,
                reason=random.choice(
                    ["Annual merit increase", "Promotion", "Market adjustment"]
                ),
            )
        )

    return employee, records


def seed(count: int, reset: bool):
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(Employee).count()
        if existing and not reset:
            print(f"Database already has {existing} employees. Use --reset to rebuild.")
            return

        batch_size = 500
        for start in range(0, count, batch_size):
            batch_employees = []
            for idx in range(start + 1, min(start + batch_size, count) + 1):
                employee, records = build_employee(idx)
                employee.salary_records = records
                batch_employees.append(employee)
            db.add_all(batch_employees)
            db.commit()
            print(f"Seeded {min(start + batch_size, count)}/{count} employees...")

        print(f"Done. {db.query(Employee).count()} employees in the database.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--reset", action="store_true", help="Drop & recreate tables first")
    args = parser.parse_args()
    seed(args.count, args.reset)
