from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class TemplateGroup(Base):
    __tablename__ = "template_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
