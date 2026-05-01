from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, employee, onboarding, task, leave, analytics, ai
from app.routers import attendance   # add this line
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Automation System", version="1.0.0")
app.include_router(attendance.router)

# CORS middleware (allows Streamlit to communicate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(onboarding.router)
app.include_router(task.router)
app.include_router(leave.router)
app.include_router(analytics.router)
app.include_router(ai.router)

@app.get("/")
def root():
    return {"message": "HR System Running", "docs": "/docs"}