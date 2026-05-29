from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey

from app.database import Base


class FormTemplate(Base):
    __tablename__ = "form_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    fields = Column(Text, default="[]")  # JSON: [{field_key, label, type, required, options}]
    is_base = Column(Boolean, default=False)  # True = common/base field set
    base_template_id = Column(Integer, ForeignKey("form_templates.id"), nullable=True)  # inherit from
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
