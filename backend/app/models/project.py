from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    project_number = Column(String(100), default="")  # 项目编号
    commission_type = Column(String(100), default="")  # 委托类别
    customer_name = Column(String(200), default="")    # 客户名称
    description = Column(Text, default="")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
