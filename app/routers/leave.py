from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, date
from app.database import get_db
from app.models.leave import Leave
from app.models.log import Log
from app.utils.auth import get_current_user, get_current_hr_user

router = APIRouter(prefix="/leaves", tags=["Leaves"])

class LeaveRequest(BaseModel):
    start_date: date   # changed from datetime to date
    end_date: date
    reason: str

@router.post("/apply")
def apply_leave(
    data: LeaveRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "employee":
        raise HTTPException(403, "Only employees can apply for leave")
    leave = Leave(
        employee_id=current_user.id,
        start_date=datetime.combine(data.start_date, datetime.min.time()),  # convert date to datetime
        end_date=datetime.combine(data.end_date, datetime.min.time()),
        reason=data.reason,
        status="pending"
    )
    db.add(leave)
    log = Log(action_type="LEAVE_APPLIED", description=f"Employee {current_user.id} applied for leave", employee_id=current_user.id)
    db.add(log)
    db.commit()
    return {"message": "Leave request submitted", "id": leave.id}

# Keep the other endpoints as they were
@router.get("/my-leaves")
def my_leaves(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    leaves = db.query(Leave).filter(Leave.employee_id == current_user.id).all()
    return leaves

@router.get("/pending")
def pending_leaves(db: Session = Depends(get_db), current_hr = Depends(get_current_hr_user)):
    leaves = db.query(Leave).filter(Leave.status == "pending").all()
    return leaves

@router.put("/{leave_id}")
def approve_leave(
    leave_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_hr = Depends(get_current_hr_user)
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(404, "Leave not found")
    leave.status = status
    db.commit()
    return {"message": f"Leave {status}"}