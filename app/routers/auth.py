from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.employee import Employee
from app.utils.auth import authenticate_user, create_access_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterHR(BaseModel):
    email: str
    first_name: str
    last_name: str
    department: str
    position: str
    password: str

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "user_id": user.id}

@router.post("/register-hr")
def register_hr(data: RegisterHR, db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.email == data.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")
    hashed = get_password_hash(data.password)
    hr = Employee(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        department=data.department,
        position=data.position,
        role="hr",
        password_hash=hashed
    )
    db.add(hr)
    db.commit()
    return {"message": "HR account created", "id": hr.id}