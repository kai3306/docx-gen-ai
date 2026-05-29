import json
import os
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.ai_task import AiTask
from app.models.document_template import DocumentTemplate
from app.models.form_data import FormData
from app.services import docx_gen
from app.core.security import get_current_user
from app.schemas.common import ApiResponse

router = APIRouter()
download_router = APIRouter()


class BatchGenerateRequest(BaseModel):
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    form_data_id: Optional[int] = None
    template_ids: list[int]
    naming_rule: str = "{doc_type}"
    project_name: Optional[str] = None
    project_product_info: Optional[str] = None
    project_version_info: Optional[str] = None
    field_values: Optional[dict] = None  # Direct field values for naming + rendering


class ReRenderRequest(BaseModel):
    doc_ids: list[int]
    task_id: int


@router.post("/generate", response_model=ApiResponse)
def batch_generate(req: BatchGenerateRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    # Resolve or auto-create project
    if req.project_id:
        project = db.query(Project).filter(Project.id == req.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
    else:
        # Don't derive project name from naming rule — that creates circular resolution bugs
        project_name = req.project_name or f"未命名项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fv = req.field_values or {}
        project = Project(
            name=project_name,
            description="",
            project_number=fv.get("ht_number", ""),
            commission_type=fv.get("class", ""),
            customer_name=fv.get("customer_name", "") or fv.get("client", ""),
        )
        db.add(project)
        db.flush()

    ai_data = {}
    if req.task_id:
        ai_task = db.query(AiTask).filter(AiTask.id == req.task_id).first()
        if ai_task and ai_task.ai_response:
            try:
                ai_data = json.loads(ai_task.ai_response)
            except json.JSONDecodeError:
                pass

    field_values = {}
    if req.field_values:
        # Direct field values from frontend (preferred)
        field_values.update(req.field_values)
    elif req.form_data_id:
        # Fallback: load from saved form data
        fd = db.query(FormData).filter(FormData.id == req.form_data_id).first()
        if fd and fd.field_values:
            try:
                field_values = json.loads(fd.field_values)
            except json.JSONDecodeError:
                pass

    # Priority: explicit req input > form field value > auto-created project default
    field_values["project_name"] = req.project_name or field_values.get("project_name") or project.name or ""
    # Add project fields for naming rule resolution and template context
    field_values["project_number"] = field_values.get("ht_number") or project.project_number or ""
    field_values["commission_type"] = field_values.get("class") or project.commission_type or ""
    field_values["customer_name"] = field_values.get("customer_name") or field_values.get("client") or project.customer_name or ""
    # Backward compat for existing Word templates
    field_values.setdefault("product_info", field_values.get("project_name", ""))
    field_values.setdefault("version_info", "")

    print(f"[DEBUG] field_values: {field_values}")
    print(f"[DEBUG] naming_rule: {req.naming_rule}")

    templates = db.query(DocumentTemplate).filter(
        DocumentTemplate.id.in_(req.template_ids)
    ).all()

    if not templates:
        raise HTTPException(status_code=400, detail="未选择模板")

    base_context = {
        "project_name": project.name,
        "project_number": project.project_number or "",
        "commission_type": project.commission_type or "",
        "customer_name": project.customer_name or "",
        "product_info": project.name or "",
        "version_info": project.project_number or "",
        "project_description": project.description,
    }
    base_context.update(ai_data)

    template_list = [{
        "id": t.id,
        "name": t.name,
        "file_path": t.file_path,
        "doc_type": t.doc_type,
    } for t in templates]

    try:
        naming_rule = req.naming_rule or "{doc_type}"
        gen_results = docx_gen.batch_generate_documents(
            templates=template_list,
            base_context=base_context,
            field_values=field_values,
            naming_rule=naming_rule,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档生成失败: {str(e)}")

    if not gen_results:
        raise HTTPException(status_code=500, detail="文档生成失败")

    # Save document records
    doc_records = []
    for r in gen_results:
        file_name = os.path.basename(r["path"])
        doc_rec = Document(
            project_id=project.id,
            doc_type=r.get("doc_type", "document"),
            file_name=file_name,
            file_path=r["path"],
            template_id=r["template_id"],
            status="generated",
        )
        db.add(doc_rec)
        doc_records.append(doc_rec)

    db.commit()
    for d in doc_records:
        db.refresh(d)

    if len(doc_records) == 1:
        d = doc_records[0]
        return ApiResponse(data={
            "mode": "single",
            "doc_ids": [d.id],
            "doc_id": d.id,
            "file_name": d.file_name,
            "project_id": project.id,
        })

    # Multiple docs: zip them
    paths = [r["path"] for r in gen_results]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"documents_{ts}.zip"
    zip_path = Path(docx_gen.settings.GENERATED_DIR) / zip_name
    zip_bytes = docx_gen.pack_to_zip(paths)
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    zip_doc = Document(
        project_id=project.id,
        doc_type="batch",
        file_name=zip_name,
        file_path=str(zip_path),
        status="generated",
    )
    db.add(zip_doc)
    db.commit()
    db.refresh(zip_doc)

    return ApiResponse(data={
        "mode": "zip",
        "doc_ids": [d.id for d in doc_records],
        "doc_id": zip_doc.id,
        "file_name": zip_name,
        "child_doc_ids": [d.id for d in doc_records],
        "project_id": project.id,
    })


@router.post("/re-render", response_model=ApiResponse)
def re_render_docs(req: ReRenderRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ai_task = db.query(AiTask).filter(AiTask.id == req.task_id).first()
    if not ai_task:
        raise HTTPException(status_code=400, detail="AI任务不存在")

    ai_data = {}
    if ai_task.ai_response:
        try:
            ai_data = json.loads(ai_task.ai_response)
        except json.JSONDecodeError:
            pass

    if not ai_data:
        raise HTTPException(status_code=400, detail="AI任务尚未生成内容")

    # Load documents and their templates
    docs = db.query(Document).filter(Document.id.in_(req.doc_ids)).all()
    if not docs:
        raise HTTPException(status_code=400, detail="文档不存在")

    # Get projects from documents
    project_ids = set(d.project_id for d in docs)
    projects = {p.id: p for p in db.query(Project).filter(Project.id.in_(project_ids)).all()}

    doc_template_pairs = []
    for d in docs:
        if not d.template_id:
            continue
        tmpl = db.query(DocumentTemplate).filter(DocumentTemplate.id == d.template_id).first()
        if not tmpl or not os.path.exists(tmpl.file_path):
            continue
        project = projects.get(d.project_id)
        doc_template_pairs.append({
            "doc_id": d.id,
            "doc_path": d.file_path,
            "template_id": tmpl.id,
            "template_path": tmpl.file_path,
            "doc_type": tmpl.doc_type,
            "project_name": project.name if project else "",
            "project_number": project.project_number if project else "",
            "commission_type": project.commission_type if project else "",
            "customer_name": project.customer_name if project else "",
        })

    if not doc_template_pairs:
        raise HTTPException(status_code=400, detail="没有可重新渲染的文档")

    # Use first doc's project for context
    first_pair = doc_template_pairs[0]
    base_context = {
        "project_name": first_pair["project_name"],
        "project_number": first_pair.get("project_number", ""),
        "commission_type": first_pair.get("commission_type", ""),
        "customer_name": first_pair.get("customer_name", ""),
    }

    # Use a default naming rule
    naming_rule = "{doc_type}"

    results = docx_gen.re_render_documents(
        doc_template_pairs=doc_template_pairs,
        base_context=base_context,
        ai_context=ai_data,
        field_values=base_context,
        naming_rule=naming_rule,
    )

    # Update document records
    for r in results:
        d = db.query(Document).get(r["doc_id"])
        if d:
            d.file_path = r["path"]
            d.file_name = os.path.basename(r["path"])
            d.ai_enhanced = 1
            d.status = "completed"

    db.commit()

    return ApiResponse(data={
        "re_rendered": len(results),
        "doc_ids": [r["doc_id"] for r in results],
    })


@router.get("", response_model=ApiResponse)
def list_documents(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    docs = db.query(Document).order_by(Document.created_at.desc()).limit(100).all()
    return ApiResponse(data=[{
        "id": d.id,
        "project_id": d.project_id,
        "doc_type": d.doc_type,
        "file_name": d.file_name,
        "status": d.status,
        "ai_enhanced": d.ai_enhanced,
        "created_at": d.created_at.isoformat(),
    } for d in docs])


@download_router.get("/{doc_id}")
def download_document(doc_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    file_path = Path(doc.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    doc.status = "downloaded"
    db.commit()

    if doc.file_name.endswith(".zip"):
        return FileResponse(
            path=str(file_path),
            filename=doc.file_name,
            media_type="application/zip",
        )
    return FileResponse(
        path=str(file_path),
        filename=doc.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
