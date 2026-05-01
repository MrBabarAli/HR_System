from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.task import Task
from app.utils.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class TaskUpdate(BaseModel):
    status: str = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str = None
    status: str
    priority: str

    class Config:
        from_attributes = True

@router.get("/employee/{employee_id}", response_model=List[TaskResponse])
def get_employee_tasks(employee_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    print(f"Fetching tasks for employee {employee_id}, current user {current_user.id}, role {current_user.role}")
    if current_user.role == "employee" and current_user.id != employee_id:
        raise HTTPException(403, "Access denied")
    tasks = db.query(Task).filter(Task.employee_id == employee_id).all()
    print(f"Found {len(tasks)} tasks")
    return tasks

@router.get("/employee/{employee_id}", response_model=List[TaskResponse])
def get_employee_tasks(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Employees can only see their own tasks
    if current_user.role == "employee" and current_user.id != employee_id:
        raise HTTPException(403, "Access denied")
    tasks = db.query(Task).filter(Task.employee_id == employee_id).all()
    return tasks

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    if update.status:
        task.status = update.status
    db.commit()
    db.refresh(task)
    return task