from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("template_groups.id"), nullable=False)
    name = Column(String(200), nullable=False)
    doc_type = Column(String(50), default="")
    file_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
