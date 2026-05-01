import httpx
import json
import re
from app.config import settings
from app.models.task import Task

async def generate_ai_tasks(employee_id: int, position: str, department: str):
    """
    Call AI to generate personalized onboarding tasks.
    Returns a list of Task objects (not yet added to DB).
    """
    prompt = f"""Generate 5 specific onboarding tasks for a new {position} in the {department} department.
Return as a JSON array of objects with "title" and "description".
Example: [{{"title": "Set up dev environment", "description": "Install VS Code, Git, Docker"}}]"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.OPENAI_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            # Extract JSON array from response (AI might wrap in markdown)
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                tasks_data = json.loads(json_match.group())
                tasks = []
                for t in tasks_data:
                    tasks.append(Task(
                        employee_id=employee_id,
                        title=t["title"],
                        description=t["description"],
                        ai_generated=True
                    ))
                return tasks
    except Exception as e:
        print(f"AI task generation error: {e}")
    
    # Fallback default tasks if AI fails
    return [
        Task(employee_id=employee_id, title="Complete personal information", description="Fill in all details", ai_generated=False),
        Task(employee_id=employee_id, title="Submit ID documents", description="Upload passport/driver license", ai_generated=False),
        Task(employee_id=employee_id, title="Review company policies", description="Read employee handbook", ai_generated=False),
        Task(employee_id=employee_id, title="Meet your manager", description="Schedule 1:1 meeting", ai_generated=False),
        Task(employee_id=employee_id, title="Set up workstation", description="Get laptop and software access", ai_generated=False),
    ]