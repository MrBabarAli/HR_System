from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx
from app.database import get_db
from app.models.employee import Employee
from app.models.log import Log
from app.config import settings
from app.utils.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])

class AIRequest(BaseModel):
    user_message: str

@router.post("/onboarding-assist/{employee_id}")
def ai_assist(
    employee_id: int,
    request: AIRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(404, "Employee not found")
    prompt = f"You are an HR onboarding assistant for {employee.first_name} {employee.last_name}, a {employee.position} in the {employee.department} department. Question: {request.user_message}"
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{settings.OPENAI_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300
                }
            )
        if resp.status_code == 200:
            answer = resp.json()["choices"][0]["message"]["content"]
        else:
            answer = "AI service is temporarily unavailable. Please try again later."
    except Exception as e:
        print(f"AI error: {e}")
        answer = "I'm your AI assistant. Please complete your pending tasks and contact HR for specific questions."
    # Log interaction
    log = Log(action_type="AI_INTERACTION", description=f"AI helped {employee.first_name}", employee_id=employee_id, performed_by="ai")
    db.add(log)
    db.commit()
    return {"response": answer}