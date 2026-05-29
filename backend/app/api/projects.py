from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.security import get_current_user

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(req: ProjectCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    project = Project(
        name=req.name,
        project_number=req.project_number or "",
        commission_type=req.commission_type or "",
        customer_name=req.customer_name or "",
        description=req.description or "",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, req: ProjectUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    db.delete(project)
    db.commit()
    return {"success": True, "message": "项目已删除"}
