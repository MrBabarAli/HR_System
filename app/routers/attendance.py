from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.utils.auth import get_current_user, get_current_hr_user

router = APIRouter(prefix="/attendance", tags=["Attendance"])

class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    status: str

    class Config:
        from_attributes = True

@router.post("/check-in")
def check_in(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    today = date.today()
    record = db.query(Attendance).filter(
        Attendance.employee_id == current_user.id,
        Attendance.date == today
    ).first()
    if record and record.check_in:
        raise HTTPException(400, "Already checked in today")
    if not record:
        record = Attendance(employee_id=current_user.id, date=today)
        db.add(record)
    record.check_in = datetime.now()
    db.commit()
    return {"message": "Checked in successfully", "time": record.check_in}

@router.post("/check-out")
def check_out(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    today = date.today()
    record = db.query(Attendance).filter(
        Attendance.employee_id == current_user.id,
        Attendance.date == today
    ).first()
    if not record or not record.check_in:
        raise HTTPException(400, "You haven't checked in today")
    if record.check_out:
        raise HTTPException(400, "Already checked out")
    record.check_out = datetime.now()
    db.commit()
    return {"message": "Checked out successfully", "time": record.check_out}

@router.get("/my-attendance")
def my_attendance(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    records = db.query(Attendance).filter(
        Attendance.employee_id == current_user.id
    ).order_by(Attendance.date.desc()).all()
    return records

@router.get("/all", response_model=List[AttendanceResponse])
def all_attendance(
    employee_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_hr = Depends(get_current_hr_user)
):
    query = db.query(Attendance)
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    return query.order_by(Attendance.date.desc()).all()