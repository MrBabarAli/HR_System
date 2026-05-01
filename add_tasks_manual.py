import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Login as HR to get token
login = requests.post(f"{BASE_URL}/auth/login", json={"email": "hr@company.com", "password": "admin123"})
if login.status_code != 200:
    print("Login failed")
    exit(1)
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. For employee 7, add tasks directly via API
employee_id = 7

tasks_data = [
    {"title": "Complete personal information", "description": "Fill in all details"},
    {"title": "Submit ID documents", "description": "Upload passport/driver license"},
    {"title": "Review company policies", "description": "Read employee handbook"},
    {"title": "Meet your manager", "description": "Schedule 1:1 meeting"},
    {"title": "Set up workstation", "description": "Get laptop and software access"},
]

for task in tasks_data:
    payload = {
        "employee_id": employee_id,
        "title": task["title"],
        "description": task["description"]
    }
    resp = requests.post(f"{BASE_URL}/tasks/", json=payload, headers=headers)
    if resp.status_code == 201:
        print(f"✅ Added: {task['title']}")
    else:
        print(f"❌ Failed: {task['title']} – {resp.text}")

print("Done.")