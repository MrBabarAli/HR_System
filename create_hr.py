import requests

resp = requests.post("http://127.0.0.1:8000/auth/register-hr", json={
    "email": "hr@company.com",
    "first_name": "Admin",
    "last_name": "HR",
    "department": "HR",
    "position": "HR Manager",
    "password": "admin123"
})
print(resp.status_code, resp.text)