from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models.onboarding import Onboarding
from app.models.task import Task
from app.models.log import Log
from app.models.employee import Employee
from app.utils.auth import get_current_user
from app.utils.email import send_onboarding_started_email

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

class OnboardingCreate(BaseModel):
    employee_id: int

class OnboardingUpdate(BaseModel):
    progress_percentage: float = None
    status: str = None

class OnboardingResponse(BaseModel):
    id: int
    employee_id: int
    status: str
    progress_percentage: float
    documents_verified: bool
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

@router.post("/", response_model=OnboardingResponse, status_code=201)
def start_onboarding(
    data: OnboardingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    print(f"\n===== START ONBOARDING for employee {data.employee_id} =====")
    
    # Check if onboarding already exists
    existing = db.query(Onboarding).filter(Onboarding.employee_id == data.employee_id).first()
    if existing:
        # Check if tasks exist
        task_count = db.query(Task).filter(Task.onboarding_id == existing.id).count()
        if task_count > 0:
            print("Onboarding and tasks already exist, returning existing")
            return existing
        else:
            print("Onboarding exists but no tasks. Proceeding to create tasks.")
            onboarding = existing
    else:
        # Create new onboarding record
        onboarding = Onboarding(employee_id=data.employee_id)
        db.add(onboarding)
        db.flush()  # assign ID without committing
        print(f"Created onboarding with id {onboarding.id}")
    
    # ----- CREATE TASKS -----
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
            employee_id=data.employee_id,
            onboarding_id=onboarding.id,
            title=title,
            description=desc,
            ai_generated=True
        )
        tasks.append(task)
    db.add_all(tasks)
    print(f"Added {len(tasks)} tasks to session")
    
    # Log the action
    log = Log(
        action_type="ONBOARDING_STARTED",
        description=f"Onboarding started for employee {data.employee_id}",
        employee_id=data.employee_id,
        performed_by="system"
    )
    db.add(log)
    
    # Commit everything
    db.commit()
    print("Committed all changes")
    
    # Verify tasks were inserted (optional)
    task_count = db.query(Task).filter(Task.onboarding_id == onboarding.id).count()
    print(f"Verified: {task_count} tasks in database for this onboarding")
    
    # Send congratulations email
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if employee:
        print(f"Sending email to {employee.email}")
        send_onboarding_started_email(
            employee.email,
            f"{employee.first_name} {employee.last_name}",
            employee.position,
            employee.department
        )
    
    print("===== ONBOARDING COMPLETE =====\n")
    return onboarding

@router.get("/employee/{employee_id}", response_model=OnboardingResponse)
def get_onboarding(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    onboarding = db.query(Onboarding).filter(Onboarding.employee_id == employee_id).first()
    if not onboarding:
        raise HTTPException(404, "Onboarding not found")
    return onboarding

@router.put("/{onboarding_id}", response_model=OnboardingResponse)
def update_onboarding(
    onboarding_id: int,
    update: OnboardingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    onboarding = db.query(Onboarding).filter(Onboarding.id == onboarding_id).first()
    if not onboarding:
        raise HTTPException(404, "Onboarding not found")
    
    if update.progress_percentage is not None:
        onboarding.progress_percentage = update.progress_percentage
        if onboarding.progress_percentage >= 100:
            onboarding.status = "completed"
            onboarding.completed_at = datetime.now()
    if update.status:
        onboarding.status = update.status
    
    db.commit()
    db.refresh(onboarding)
    return onboarding