import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.form_data import FormData
from app.schemas.form import FormDataCreate, FormDataUpdate
from app.core.security import get_current_user
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("", response_model=ApiResponse)
def list_form_data(
    project_id: int = Query(None),
    form_template_id: int = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(FormData)
    if project_id:
        query = query.filter(FormData.project_id == project_id)
    if form_template_id:
        query = query.filter(FormData.form_template_id == form_template_id)
    items = query.order_by(FormData.created_at.desc()).all()
    result = []
    for d in items:
        result.append({
            "id": d.id,
            "form_template_id": d.form_template_id,
            "project_id": d.project_id,
            "field_values": json.loads(d.field_values) if d.field_values else {},
            "created_at": d.created_at.isoformat(),
        })
    return ApiResponse(data=result)


@router.post("", response_model=ApiResponse)
def create_form_data(req: FormDataCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    fd = FormData(
        form_template_id=req.form_template_id,
        project_id=req.project_id,
        field_values=json.dumps(req.field_values, ensure_ascii=False),
    )
    db.add(fd)
    db.commit()
    db.refresh(fd)
    return ApiResponse(data={"id": fd.id})


@router.get("/{data_id}", response_model=ApiResponse)
def get_form_data(data_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    fd = db.query(FormData).filter(FormData.id == data_id).first()
    if not fd:
        raise HTTPException(status_code=404, detail="表单数据不存在")
    return ApiResponse(data={
        "id": fd.id,
        "form_template_id": fd.form_template_id,
        "project_id": fd.project_id,
        "field_values": json.loads(fd.field_values) if fd.field_values else {},
        "created_at": fd.created_at.isoformat(),
    })


@router.put("/{data_id}", response_model=ApiResponse)
def update_form_data(data_id: int, req: FormDataUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    fd = db.query(FormData).filter(FormData.id == data_id).first()
    if not fd:
        raise HTTPException(status_code=404, detail="表单数据不存在")
    if req.field_values is not None:
        fd.field_values = json.dumps(req.field_values, ensure_ascii=False)
    db.commit()
    return ApiResponse(message="更新成功")
