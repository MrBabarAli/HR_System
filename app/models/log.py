from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    employee_id = Column(Integer, nullable=True)
    performed_by = Column(String, default="system")
    created_at = Column(DateTime(timezone=True), server_default=func.now())