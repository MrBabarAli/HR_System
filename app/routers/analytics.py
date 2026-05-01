from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.employee import Employee
from app.models.onboarding import Onboarding
from app.models.task import Task
from app.models.log import Log
from app.utils.auth import get_current_hr_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), current_hr = Depends(get_current_hr_user)):
    total_employees = db.query(Employee).count()
    active_employees = db.query(Employee).filter(Employee.status == "active").count()
    total_onboarding = db.query(Onboarding).count()
    completed_onboarding = db.query(Onboarding).filter(Onboarding.status == "completed").count()
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()
    return {
        "employees": {
            "total": total_employees,
            "active": active_employees
        },
        "onboarding": {
            "total": total_onboarding,
            "completed": completed_onboarding,
            "completion_rate": (completed_onboarding / total_onboarding * 100) if total_onboarding else 0
        },
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks else 0
        }
    }

@router.get("/logs")
def get_logs(db: Session = Depends(get_db), current_hr = Depends(get_current_hr_user)):
    return db.query(Log).order_by(Log.created_at.desc()).limit(100).all()