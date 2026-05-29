from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    doc_type = Column(String(50), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    template_id = Column(Integer, nullable=True)
    ai_enhanced = Column(Integer, default=0)
    status = Column(String(20), default="generated")
    created_at = Column(DateTime, default=datetime.utcnow)
