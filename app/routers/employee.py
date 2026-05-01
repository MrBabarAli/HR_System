from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.employee import Employee
from app.models.onboarding import Onboarding
from app.models.log import Log
from app.models.task import Task
from app.utils.auth import get_password_hash, get_current_hr_user
from app.utils.email import send_welcome_email

router = APIRouter(prefix="/employees", tags=["Employees"])

class EmployeeCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    department: str
    position: str
    phone: str = None
    password: str

class EmployeeResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    department: str
    position: str
    status: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    emp: EmployeeCreate,
    db: Session = Depends(get_db),
    current_hr = Depends(get_current_hr_user)
):
    # Check if email already exists
    existing = db.query(Employee).filter(Employee.email == emp.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    
    # Hash password and create employee
    hashed = get_password_hash(emp.password)
    db_emp = Employee(
        email=emp.email,
        first_name=emp.first_name,
        last_name=emp.last_name,
        department=emp.department,
        position=emp.position,
        phone=emp.phone,
        password_hash=hashed,
        role="employee"
    )
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    
    # Auto-create onboarding record
    onboarding = Onboarding(employee_id=db_emp.id)
    db.add(onboarding)
    db.flush()
    
    # Auto-assign onboarding tasks
    tasks_data = [
        ("Complete personal information", "Fill in all details"),
        ("Submit ID documents", "Upload passport/driver license"),
        ("Review company policies", "Read employee handbook"),
        ("Meet your manager", "Schedule 1:1 meeting"),
        ("Set up workstation", "Get laptop and software access"),
    ]
    tasks = []
    for title, desc in tasks_data:
        task = Task(
            employee_id=db_emp.id,
            onboarding_id=onboarding.id,
            title=title,
            description=desc,
            ai_generated=True
        )
        tasks.append(task)
    db.add_all(tasks)
    
    # Log the action
    log = Log(
        action_type="EMPLOYEE_JOINED",
        description=f"New employee {db_emp.first_name} {db_emp.last_name} joined",
        employee_id=db_emp.id,
        performed_by="hr"
    )
    db.add(log)
    db.commit()
    
    # Send welcome email
    send_welcome_email(
        db_emp.email,
        f"{db_emp.first_name} {db_emp.last_name}",
        db_emp.position,
        db_emp.department
    )
    
    return db_emp

@router.get("/", response_model=List[EmployeeResponse])
def get_employees(
    db: Session = Depends(get_db),
    current_hr = Depends(get_current_hr_user)
):
    return db.query(Employee).all()

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_hr = Depends(get_current_hr_user)
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp