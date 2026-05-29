from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.database import Base


class AiTask(Base):
    __tablename__ = "ai_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    task_type = Column(String(50), nullable=False)
    source_content = Column(Text, default="")
    source_format = Column(String(20), default="")
    ai_response = Column(Text, default="")
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
