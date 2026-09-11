import datetime as dt

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Employee(Base):
    """
    An employee record. Compensation is intentionally NOT a column here — see
    SalaryRecord. This table only holds facts that change rarely and don't need
    a history trail.
    """

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(20), unique=True, index=True, nullable=False)

    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)

    department = Column(String(50), nullable=False, index=True)
    job_title = Column(String(100), nullable=False)
    job_level = Column(String(30), nullable=False, index=True)

    country = Column(String(60), nullable=False, index=True)
    currency = Column(String(3), nullable=False)

    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    status = Column(String(10), nullable=False, default="active", index=True)
    hire_date = Column(Date, nullable=False)

    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    salary_records = relationship(
        "SalaryRecord",
        back_populates="employee",
        cascade="all, delete-orphan",
        order_by="desc(SalaryRecord.effective_date)",
    )

    __table_args__ = (
        Index("ix_employees_dept_country", "department", "country"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class SalaryRecord(Base):
    """
    One dated compensation entry for an employee. The *current* salary is simply
    the record with the most recent effective_date <= today — we never overwrite
    a row in place. This gives HR a legally-useful audit trail for free and makes
    "give a raise" an INSERT instead of an UPDATE.
    """

    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)

    base_salary = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    bonus_target_pct = Column(Float, nullable=False, default=0.0)

    effective_date = Column(Date, nullable=False, index=True)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=dt.datetime.utcnow)

    employee = relationship("Employee", back_populates="salary_records")

    __table_args__ = (
        Index("ix_salary_employee_effective", "employee_id", "effective_date"),
    )
