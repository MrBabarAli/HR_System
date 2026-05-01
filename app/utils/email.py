import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

def send_welcome_email(employee_email: str, employee_name: str, position: str, department: str):
    """Email sent when employee is first added to the system"""
    subject = f"Welcome to the team, {employee_name}!"
    body = f"""
Dear {employee_name},

Congratulations and welcome! You've been added as a {position} in the {department} department.

Please log in to the HR portal to start your onboarding. Your AI assistant will guide you through tasks.

Best regards,
HR Automation Team
"""
    msg = MIMEMultipart()
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = employee_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Welcome email error: {e}")
        return False

def send_onboarding_started_email(employee_email: str, employee_name: str, position: str, department: str):
    """Email sent when onboarding process is officially started"""
    subject = f"🎉 Your Onboarding Has Started, {employee_name}!"
    body = f"""
Dear {employee_name},

Great news! Your onboarding process has officially started for the position of {position} in the {department} department.

Here's what you need to do next:
✅ Log in to the HR portal
✅ Complete your personal information
✅ Submit your ID documents
✅ Review company policies
✅ Complete your assigned tasks

Your AI assistant is available 24/7 to answer any questions.

We're excited to have you on board!

Best regards,
HR Automation Team
"""
    msg = MIMEMultipart()
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = employee_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Onboarding email error: {e}")
        return False