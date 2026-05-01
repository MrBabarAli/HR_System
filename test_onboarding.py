import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 1. Login as HR to get token
login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "hr@company.com", "password": "admin123"})
if login_resp.status_code != 200:
    print("HR login failed")
    exit()
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("HR logged in, token obtained")

# 2. Create a new employee (with a unique email)
import time
employee_data = {
    "email": f"testemployee_{int(time.time())}@example.com",
    "first_name": "Test",
    "last_name": "User",
    "department": "Engineering",
    "position": "Software Engineer",
    "password": "test123"
}
create_emp = requests.post(f"{BASE_URL}/employees/", json=employee_data, headers=headers)
if create_emp.status_code != 201:
    print("Failed to create employee", create_emp.text)
    exit()
emp_id = create_emp.json()["id"]
print(f"Employee created with id {emp_id}")

# 3. Start onboarding for that employee
onboarding_data = {"employee_id": emp_id}
start_ob = requests.post(f"{BASE_URL}/onboarding/", json=onboarding_data, headers=headers)
if start_ob.status_code != 201:
    print("Failed to start onboarding", start_ob.text)
    # If already exists, it's fine
else:
    print("Onboarding started")

# 4. Get tasks for the employee (as HR)
tasks_resp = requests.get(f"{BASE_URL}/tasks/employee/{emp_id}", headers=headers)
if tasks_resp.status_code == 200:
    tasks = tasks_resp.json()
    print(f"Found {len(tasks)} tasks for employee {emp_id}")
    for t in tasks:
        print(f" - {t['title']}: {t.get('description', '')}")
else:
    print("Could not fetch tasks", tasks_resp.text)