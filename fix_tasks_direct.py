from app.database import SessionLocal
from app.models.task import Task
from app.models.onboarding import Onboarding

db = SessionLocal()

# Get all onboarding records
onboardings = db.query(Onboarding).all()
print(f"Found {len(onboardings)} onboarding records.")

for ob in onboardings:
    # Check if employee already has tasks
    existing = db.query(Task).filter(Task.employee_id == ob.employee_id).first()
    if existing:
        print(f"Employee {ob.employee_id} already has tasks. Skipping.")
        continue

    print(f"Adding tasks for employee {ob.employee_id} (onboarding {ob.id})")
    tasks = [
        Task(employee_id=ob.employee_id, onboarding_id=ob.id,
             title="Complete personal information", description="Fill in all your personal details", ai_generated=True),
        Task(employee_id=ob.employee_id, onboarding_id=ob.id,
             title="Submit ID documents", description="Upload passport, driver's license, or ID card", ai_generated=True),
        Task(employee_id=ob.employee_id, onboarding_id=ob.id,
             title="Review company policies", description="Read and acknowledge the employee handbook", ai_generated=True),
        Task(employee_id=ob.employee_id, onboarding_id=ob.id,
             title="Meet your manager", description="Schedule a 1:1 introductory meeting", ai_generated=True),
        Task(employee_id=ob.employee_id, onboarding_id=ob.id,
             title="Set up workstation", description="Get laptop, software, and access credentials", ai_generated=True),
    ]
    db.add_all(tasks)
    db.commit()
    print(f"  Added {len(tasks)} tasks.")

db.close()
print("Done.")