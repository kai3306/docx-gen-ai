from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey

from app.database import Base


class FormData(Base):
    __tablename__ = "form_data"

    id = Column(Integer, primary_key=True, index=True)
    form_template_id = Column(Integer, ForeignKey("form_templates.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    field_values = Column(Text, default="{}")  # JSON: {field_key: value}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
