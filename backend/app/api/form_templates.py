import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.form_template import FormTemplate
from app.schemas.form import FormTemplateCreate, FormTemplateUpdate, FormTemplateResponse
from app.core.security import get_current_user
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("", response_model=ApiResponse)
def list_form_templates(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    templates = db.query(FormTemplate).order_by(FormTemplate.created_at.desc()).all()
    result = []
    for t in templates:
        base_name = None
        if t.base_template_id:
            base = db.query(FormTemplate).filter(FormTemplate.id == t.base_template_id).first()
            base_name = base.name if base else None
        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "fields": json.loads(t.fields) if t.fields else [],
            "is_base": t.is_base,
            "base_template_id": t.base_template_id,
            "base_template_name": base_name,
            "created_at": t.created_at.isoformat(),
        })
    return ApiResponse(data=result)


@router.get("/bases", response_model=ApiResponse)
def list_base_templates(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """List only base/common field templates."""
    templates = db.query(FormTemplate).filter(FormTemplate.is_base == True).order_by(FormTemplate.created_at.desc()).all()
    return ApiResponse(data=[{
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "fields": json.loads(t.fields) if t.fields else [],
    } for t in templates])


@router.post("", response_model=ApiResponse)
def create_form_template(req: FormTemplateCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    # If inheriting from a base template, merge fields
    fields = [f.dict() for f in req.fields]
    if req.base_template_id:
        base = db.query(FormTemplate).filter(
            FormTemplate.id == req.base_template_id,
            FormTemplate.is_base == True,
        ).first()
        if base:
            base_fields = json.loads(base.fields) if base.fields else []
            # Prepend inherited fields (child's own fields override if same key)
            existing_keys = {f["field_key"] for f in fields}
            inherited = [f for f in base_fields if f["field_key"] not in existing_keys]
            fields = inherited + fields

    template = FormTemplate(
        name=req.name,
        description=req.description,
        fields=json.dumps(fields, ensure_ascii=False),
        is_base=req.is_base,
        base_template_id=req.base_template_id,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return ApiResponse(data={"id": template.id})


@router.get("/{template_id}", response_model=ApiResponse)
def get_form_template(template_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="表单模板不存在")
    base_name = None
    if template.base_template_id:
        base = db.query(FormTemplate).filter(FormTemplate.id == template.base_template_id).first()
        base_name = base.name if base else None
    return ApiResponse(data={
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "fields": json.loads(template.fields) if template.fields else [],
        "is_base": template.is_base,
        "base_template_id": template.base_template_id,
        "base_template_name": base_name,
        "created_at": template.created_at.isoformat(),
    })


@router.put("/{template_id}", response_model=ApiResponse)
def update_form_template(template_id: int, req: FormTemplateUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="表单模板不存在")
    if req.name is not None:
        template.name = req.name
    if req.description is not None:
        template.description = req.description
    if req.fields is not None:
        fields = [f.dict() for f in req.fields]
        # Re-merge base fields if inheriting
        if template.base_template_id:
            base = db.query(FormTemplate).filter(
                FormTemplate.id == template.base_template_id,
                FormTemplate.is_base == True,
            ).first()
            if base:
                base_fields = json.loads(base.fields) if base.fields else []
                existing_keys = {f["field_key"] for f in fields}
                inherited = [f for f in base_fields if f["field_key"] not in existing_keys]
                fields = inherited + fields
        template.fields = json.dumps(fields, ensure_ascii=False)
    if req.is_base is not None:
        template.is_base = req.is_base
    if req.base_template_id is not None:
        template.base_template_id = req.base_template_id
    db.commit()
    return ApiResponse(message="更新成功")


@router.delete("/{template_id}", response_model=ApiResponse)
def delete_form_template(template_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="表单模板不存在")
    db.delete(template)
    db.commit()
    return ApiResponse(message="删除成功")
