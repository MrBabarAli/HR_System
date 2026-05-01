import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

API_URL = "http://127.0.0.1:8000"

# Session state
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

st.set_page_config(page_title="HR System", layout="wide")

def api_call(method, endpoint, data=None, params=None):
    """API call with optional query parameters."""
    url = f"{API_URL}/{endpoint}"
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            r = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            r = requests.put(url, json=data, headers=headers)
        else:
            return None
        if r.status_code in (200, 201, 204):
            return r.json() if r.text else {}
        else:
            st.error(f"Error {r.status_code}: {r.text[:200]}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

# ------------------- LOGIN -------------------
if not st.session_state.token:
    st.title("🔐 HR Automation Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": pwd})
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.session_state.user_id = data["user_id"]
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# ------------------- SIDEBAR -------------------
st.sidebar.title(f"Welcome, {st.session_state.role.upper()}")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ------------------- ROLE MENU -------------------
if st.session_state.role == "hr":
    menu = st.sidebar.radio("Menu", [
        "Dashboard", "Employees", "Onboarding", "Leaves", "Attendance", "Analytics", "AI"
    ])
else:
    menu = st.sidebar.radio("Menu", [
        "My Dashboard", "My Tasks", "My Leaves", "My Attendance", "AI"
    ])

# ==================== HR VIEWS ====================
if st.session_state.role == "hr":
    if menu == "Dashboard":
        st.header("HR Dashboard")
        stats = api_call("GET", "analytics/dashboard")
        if stats:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Employees", stats["employees"]["total"])
            col2.metric("Active", stats["employees"]["active"])
            col3.metric("Onboarding Rate", f"{stats['onboarding']['completion_rate']:.1f}%")
        st.subheader("Recent Employees")
        emps = api_call("GET", "employees/")
        if emps:
            df = pd.DataFrame(emps)
            st.dataframe(df[["id","first_name","last_name","email","department","status"]])

    elif menu == "Employees":
        st.header("Manage Employees")
        with st.form("add_employee"):
            col1, col2 = st.columns(2)
            with col1:
                fn = st.text_input("First Name")
                ln = st.text_input("Last Name")
                email = st.text_input("Email")
                pwd = st.text_input("Password", type="password")
            with col2:
                dept = st.selectbox("Department", ["Engineering","Sales","Marketing","HR","Finance"])
                pos = st.text_input("Position")
                phone = st.text_input("Phone")
            if st.form_submit_button("Add Employee"):
                data = {"first_name":fn,"last_name":ln,"email":email,"password":pwd,"department":dept,"position":pos,"phone":phone}
                res = api_call("POST", "employees/", data)
                if res:
                    st.success(f"Added {res['first_name']} (welcome email sent)")
                    st.rerun()
        st.subheader("All Employees")
        emps = api_call("GET", "employees/")
        if emps:
            st.dataframe(pd.DataFrame(emps))

    elif menu == "Onboarding":
        st.header("Onboarding Progress")
        emps = api_call("GET", "employees/")
        if emps:
            for emp in emps:
                onb = api_call("GET", f"onboarding/employee/{emp['id']}")
                if onb:
                    prog = onb.get("progress_percentage", 0)
                    with st.expander(f"{emp['first_name']} {emp['last_name']} - {prog}%"):
                        st.progress(prog/100)
                        if st.button(f"+20%", key=f"prog_{emp['id']}"):
                            new_prog = min(prog+20, 100)
                            api_call("PUT", f"onboarding/{onb['id']}", {"progress_percentage": new_prog})
                            st.rerun()
                else:
                    with st.expander(f"{emp['first_name']} {emp['last_name']} - Not started"):
                        if st.button("Start Onboarding", key=f"start_{emp['id']}"):
                            api_call("POST", "onboarding/", {"employee_id": emp['id']})
                            st.rerun()

    elif menu == "Leaves":
        st.header("Pending Leave Requests")
        leaves = api_call("GET", "leaves/pending")
        if leaves:
            for l in leaves:
                emp = api_call("GET", f"employees/{l['employee_id']}")
                if emp:
                    with st.expander(f"{emp['first_name']} {emp['last_name']} - {l['start_date'][:10]}"):
                        st.write(l['reason'])
                        col1, col2 = st.columns(2)
                        if col1.button("Approve", key=f"app_{l['id']}"):
                            api_call("PUT", f"leaves/{l['id']}?status=approved", None)
                            st.rerun()
                        if col2.button("Reject", key=f"rej_{l['id']}"):
                            api_call("PUT", f"leaves/{l['id']}?status=rejected", None)
                            st.rerun()
        else:
            st.info("No pending leaves")

    # ========== HR ATTENDANCE ==========
    elif menu == "Attendance":
        st.header("📊 Employee Attendance")
        employees = api_call("GET", "employees/")
        emp_options = {0: "All Employees"}
        if employees:
            for e in employees:
                emp_options[e["id"]] = f"{e['first_name']} {e['last_name']}"
        selected_emp = st.selectbox("Filter by Employee", list(emp_options.keys()), format_func=lambda x: emp_options[x])

        col1, col2 = st.columns(2)
        start_date = col1.date_input("Start Date", value=date(2026, 1, 1))
        end_date = col2.date_input("End Date", value=date.today())

        params = {}
        if selected_emp != 0:
            params["employee_id"] = selected_emp
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        attendance = api_call("GET", "attendance/all", params=params)
        if attendance:
            df = pd.DataFrame(attendance)
            # Convert date columns for nice display
            df["date"] = pd.to_datetime(df["date"]).dt.date
            st.dataframe(df[["employee_id", "date", "check_in", "check_out", "status"]])
        else:
            st.info("No attendance records found for the selected filters.")

    elif menu == "Analytics":
        st.header("Analytics")
        stats = api_call("GET", "analytics/dashboard")
        if stats:
            col1, col2 = st.columns(2)
            col1.metric("Total Employees", stats["employees"]["total"])
            col1.metric("Completed Onboarding", stats["onboarding"]["completed"])
            col2.metric("Active Employees", stats["employees"]["active"])
            col2.metric("Tasks Completed", stats["tasks"]["completed"])
        logs = api_call("GET", "analytics/logs")
        if logs:
            st.subheader("System Logs")
            st.dataframe(pd.DataFrame(logs))

    elif menu == "AI":
        st.header("AI Assistant")
        emps = api_call("GET", "employees/")
        if emps:
            emp_dict = {e["id"]: f"{e['first_name']} {e['last_name']}" for e in emps}
            emp_id = st.selectbox("Select Employee", list(emp_dict.keys()), format_func=lambda x: emp_dict[x])
            q = st.text_area("Ask a question about onboarding or HR policies")
            if st.button("Ask AI"):
                res = api_call("POST", f"ai/onboarding-assist/{emp_id}", {"user_message": q})
                if res:
                    st.success(res["response"])

# ==================== EMPLOYEE VIEWS ====================
else:
    if menu == "My Dashboard":
        st.header("Employee Dashboard")
        # Pending tasks
        tasks = api_call("GET", f"tasks/employee/{st.session_state.user_id}")
        pending = len([t for t in tasks if t["status"] != "completed"]) if tasks else 0
        st.metric("Pending Tasks", pending)

        # Today's attendance & check-in/out
        st.subheader("📅 Today's Attendance")
        attendance_records = api_call("GET", "attendance/my-attendance")
        today_str = date.today().isoformat()
        today_record = None
        if attendance_records:
            for rec in attendance_records:
                if rec["date"] == today_str:
                    today_record = rec
                    break
        if today_record:
            st.write(f"**Check‑in:** {today_record.get('check_in', 'Not recorded')}")
            st.write(f"**Check‑out:** {today_record.get('check_out', 'Not recorded')}")
            st.write(f"**Status:** {today_record.get('status', 'present')}")
        else:
            st.info("No attendance record for today. Please check in.")

        col1, col2 = st.columns(2)
        if col1.button("✅ Check In"):
            res = api_call("POST", "attendance/check-in")
            if res:
                st.success(res.get("message", "Checked in successfully"))
                st.rerun()
        if col2.button("❌ Check Out"):
            res = api_call("POST", "attendance/check-out")
            if res:
                st.success(res.get("message", "Checked out successfully"))
                st.rerun()

    elif menu == "My Tasks":
        st.header("My Tasks")
        tasks = api_call("GET", f"tasks/employee/{st.session_state.user_id}")
        if tasks:
            for t in tasks:
                col1, col2 = st.columns([3,1])
                col1.write(f"**{t['title']}** – {t.get('description', '')}")
                status = col2.selectbox("Status", ["pending","in_progress","completed"], index=["pending","in_progress","completed"].index(t["status"]), key=f"task_{t['id']}")
                if status != t["status"]:
                    api_call("PUT", f"tasks/{t['id']}", {"status": status})
                    st.rerun()
        else:
            st.info("No tasks assigned")

    elif menu == "My Leaves":
        st.header("Apply for Leave")
        with st.form("leave_form"):
            start = st.date_input("Start Date")
            end = st.date_input("End Date")
            reason = st.text_area("Reason")
            if st.form_submit_button("Submit"):
                data = {"start_date": start.isoformat(), "end_date": end.isoformat(), "reason": reason}
                res = api_call("POST", "leaves/apply", data)
                if res:
                    st.success("Leave request submitted")
                    st.rerun()
        st.subheader("My Leave History")
        leaves = api_call("GET", "leaves/my-leaves")
        if leaves:
            df = pd.DataFrame(leaves)
            st.dataframe(df)

    # ========== EMPLOYEE ATTENDANCE HISTORY ==========
    elif menu == "My Attendance":
        st.header("📆 My Attendance History")
        records = api_call("GET", "attendance/my-attendance")
        if records:
            df = pd.DataFrame(records)
            df["date"] = pd.to_datetime(df["date"]).dt.date
            st.dataframe(df[["date", "check_in", "check_out", "status"]])
        else:
            st.info("No attendance records found.")

    elif menu == "AI":
        st.header("AI Assistant")
        q = st.text_area("Ask anything about your onboarding or tasks")
        if st.button("Ask AI"):
            res = api_call("POST", f"ai/onboarding-assist/{st.session_state.user_id}", {"user_message": q})
            if res:
                st.success(res["response"])