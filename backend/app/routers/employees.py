import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=schemas.PaginatedEmployees)
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    department: Optional[str] = None,
    country: Optional[str] = None,
    job_level: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    items, total = crud.list_employees(
        db,
        page=page,
        page_size=page_size,
        department=department,
        country=country,
        job_level=job_level,
        status=status,
        search=search,
    )
    return schemas.PaginatedEmployees(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.post("", response_model=schemas.EmployeeDetail, status_code=201)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    employee = crud.create_employee(db, payload)
    return crud.get_employee(db, employee.id)


@router.get("/{employee_id}", response_model=schemas.EmployeeDetail)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.patch("/{employee_id}", response_model=schemas.EmployeeDetail)
def update_employee(
    employee_id: int, payload: schemas.EmployeeUpdate, db: Session = Depends(get_db)
):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    crud.update_employee(db, employee, payload)
    return crud.get_employee(db, employee_id)


@router.delete("/{employee_id}", response_model=schemas.EmployeeDetail)
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)):
    """Soft delete: marks the employee inactive. Salary history is preserved."""
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    crud.deactivate_employee(db, employee)
    return crud.get_employee(db, employee_id)


@router.post(
    "/{employee_id}/salary-records",
    response_model=schemas.SalaryRecordOut,
    status_code=201,
)
def add_salary_record(
    employee_id: int, payload: schemas.SalaryRecordCreate, db: Session = Depends(get_db)
):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.add_salary_record(db, employee, payload)
