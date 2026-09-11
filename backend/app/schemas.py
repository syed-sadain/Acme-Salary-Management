import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Salary ----------

class SalaryRecordBase(BaseModel):
    base_salary: float = Field(..., gt=0, description="Annual base salary, in `currency`")
    currency: str = Field(..., min_length=3, max_length=3)
    bonus_target_pct: float = Field(0.0, ge=0, le=100)
    effective_date: dt.date
    reason: Optional[str] = None


class SalaryRecordCreate(SalaryRecordBase):
    pass


class SalaryRecordOut(SalaryRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    created_at: dt.datetime


# ---------- Employee ----------

class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=80)
    last_name: str = Field(..., min_length=1, max_length=80)
    email: EmailStr
    department: str
    job_title: str = Field(..., min_length=1, max_length=100)
    job_level: str
    country: str
    manager_id: Optional[int] = None
    hire_date: dt.date
    status: str = "active"


class EmployeeCreate(EmployeeBase):
    # Every new employee must start with an initial salary record.
    starting_salary: SalaryRecordCreate


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    job_level: Optional[str] = None
    country: Optional[str] = None
    manager_id: Optional[int] = None
    status: Optional[str] = None


class EmployeeListItem(BaseModel):
    """Slim shape used for the paginated directory list (avoids N+1 salary joins)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    department: str
    job_title: str
    job_level: str
    country: str
    status: str
    current_salary: Optional[float] = None
    currency: Optional[str] = None


class EmployeeDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    department: str
    job_title: str
    job_level: str
    country: str
    currency: str
    manager_id: Optional[int]
    status: str
    hire_date: dt.date
    salary_records: List[SalaryRecordOut] = []


class PaginatedEmployees(BaseModel):
    items: List[EmployeeListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------- Analytics ----------

class GroupAverage(BaseModel):
    group: str
    headcount: int
    avg_salary: float
    median_salary: float
    total_cost: float
    currency: Optional[str] = None


class HistogramBucket(BaseModel):
    range_start: float
    range_end: float
    count: int


class AnalyticsSummary(BaseModel):
    total_employees: int
    active_employees: int
    inactive_employees: int
    by_department: List[GroupAverage]
    by_country: List[GroupAverage]
    by_level: List[GroupAverage]
    # Distribution of each employee's salary expressed as a multiple of their own
    # country's L1 base salary (a "pay index"), NOT a currency conversion. This lets
    # us show one org-wide shape without pretending to convert INR/USD/EUR/etc. into
    # a single currency (see REQUIREMENTS.md — FX conversion is deliberately out of
    # scope). A value of 2.0 means "twice that country's entry-level base pay".
    pay_index_histogram: List[HistogramBucket]
