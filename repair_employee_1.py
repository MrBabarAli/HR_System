from app.database import SessionLocal
from app.models.employee import Employee
from app.models.onboarding import Onboarding
from app.models.task import Task

db = SessionLocal()

# Find employee 1
emp = db.query(Employee).filter(Employee.id == 1).first()
if not emp:
    print("Employee 1 not found.")
    exit(1)

# Check if onboarding already exists
onboarding = db.query(Onboarding).filter(Onboarding.employee_id == 1).first()
if not onboarding:
    onboarding = Onboarding(employee_id=1)
    db.add(onboarding)
    db.flush()
    print(f"Created onboarding record {onboarding.id}")

# Check if tasks already exist
tasks_exist = db.query(Task).filter(Task.employee_id == 1).first()
if tasks_exist:
    print("Tasks already exist. Skipping.")
else:
    tasks_data = [
        ("Complete personal information", "Fill in all your personal details"),
        ("Submit ID documents", "Upload passport, driver's license, or ID card"),
        ("Review company policies", "Read and acknowledge the employee handbook"),
        ("Meet your manager", "Schedule a 1:1 introductory meeting"),
        ("Set up workstation", "Get laptop, software, and access credentials"),
    ]
    for title, desc in tasks_data:
        task = Task(
            employee_id=1,
            onboarding_id=onboarding.id,
            title=title,
            description=desc,
            ai_generated=True
        )
        db.add(task)
    print(f"Added {len(tasks_data)} tasks.")

db.commit()
db.close()
print("Done. Employee 1 now has onboarding and tasks.")