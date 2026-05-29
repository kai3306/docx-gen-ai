import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.template_group import TemplateGroup
from app.models.document_template import DocumentTemplate
from app.schemas.template import TemplateGroupCreate, TemplateGroupUpdate
from app.core.security import get_current_user
from app.core.config import settings
from app.schemas.common import ApiResponse

router = APIRouter()

ALLOWED_TEMPLATE_EXT = {".docx"}


@router.get("", response_model=ApiResponse)
def list_template_groups(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    groups = db.query(TemplateGroup).order_by(TemplateGroup.created_at.desc()).all()
    result = []
    for g in groups:
        templates = db.query(DocumentTemplate).filter(DocumentTemplate.group_id == g.id).all()
        result.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "template_count": len(templates),
            "created_at": g.created_at.isoformat(),
        })
    return ApiResponse(data=result)


@router.post("", response_model=ApiResponse)
def create_template_group(req: TemplateGroupCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    group = TemplateGroup(name=req.name, description=req.description)
    db.add(group)
    db.commit()
    db.refresh(group)
    return ApiResponse(data={"id": group.id})


@router.get("/{group_id}", response_model=ApiResponse)
def get_template_group(group_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    group = db.query(TemplateGroup).filter(TemplateGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="模板组不存在")
    templates = db.query(DocumentTemplate).filter(DocumentTemplate.group_id == group_id).all()
    return ApiResponse(data={
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_at": group.created_at.isoformat(),
        "templates": [{
            "id": t.id,
            "name": t.name,
            "doc_type": t.doc_type,
            "file_name": t.file_name,
            "file_path": t.file_path,
            "created_at": t.created_at.isoformat(),
        } for t in templates],
    })


@router.put("/{group_id}", response_model=ApiResponse)
def update_template_group(group_id: int, req: TemplateGroupUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    group = db.query(TemplateGroup).filter(TemplateGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="模板组不存在")
    if req.name is not None:
        group.name = req.name
    if req.description is not None:
        group.description = req.description
    db.commit()
    return ApiResponse(message="更新成功")


@router.delete("/{group_id}", response_model=ApiResponse)
def delete_template_group(group_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    group = db.query(TemplateGroup).filter(TemplateGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="模板组不存在")
    # Delete all templates in group
    templates = db.query(DocumentTemplate).filter(DocumentTemplate.group_id == group_id).all()
    for t in templates:
        file_path = Path(t.file_path)
        if file_path.exists():
            file_path.unlink()
        db.delete(t)
    db.delete(group)
    db.commit()
    return ApiResponse(message="删除成功")


@router.post("/{group_id}/templates", response_model=ApiResponse)
async def upload_template(
    group_id: int,
    name: str = Form(""),
    doc_type: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    group = db.query(TemplateGroup).filter(TemplateGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="模板组不存在")

    ext = Path(file.filename).suffix.lower()
    if ext != ".docx":
        raise HTTPException(status_code=400, detail="仅支持 .docx 模板文件")

    template_dir = Path(settings.TEMPLATE_DIR) / "custom"
    template_dir.mkdir(parents=True, exist_ok=True)

    save_name = f"{uuid.uuid4()}{ext}"
    save_path = template_dir / save_name

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    if not name:
        name = Path(file.filename).stem

    dt = DocumentTemplate(
        group_id=group_id,
        name=name,
        doc_type=doc_type,
        file_name=file.filename,
        file_path=str(save_path),
    )
    db.add(dt)
    db.commit()
    db.refresh(dt)

    return ApiResponse(data={
        "id": dt.id,
        "name": dt.name,
        "doc_type": dt.doc_type,
        "file_name": dt.file_name,
    })


@router.delete("/{group_id}/templates/{template_id}", response_model=ApiResponse)
def delete_template(group_id: int, template_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    dt = db.query(DocumentTemplate).filter(
        DocumentTemplate.id == template_id,
        DocumentTemplate.group_id == group_id,
    ).first()
    if not dt:
        raise HTTPException(status_code=404, detail="模板不存在")
    file_path = Path(dt.file_path)
    if file_path.exists():
        file_path.unlink()
    db.delete(dt)
    db.commit()
    return ApiResponse(message="删除成功")
