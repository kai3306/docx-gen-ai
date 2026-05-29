import json
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ai_task import AiTask
from app.models.document import Document
from app.models.document_template import DocumentTemplate
from app.models.project import Project
from app.services import docx_gen
from app.schemas.common import ApiResponse

router = APIRouter()


class DifyCallbackRequest(BaseModel):
    ai_response: dict
    doc_ids: list[int]
    template_ids: list[int]
    naming_rule: str = "{doc_type}"


@router.post("/callback/{task_id}", response_model=ApiResponse)
def dify_callback(
    task_id: int,
    req: DifyCallbackRequest,
    db: Session = Depends(get_db),
):
    """
    Dify workflow callback endpoint.
    Dify calls this after AI generation completes to trigger secondary document rendering.
    No auth required — this is an internal service-to-service endpoint.
    """
    ai_task = db.query(AiTask).filter(AiTask.id == task_id).first()
    if not ai_task:
        raise HTTPException(status_code=404, detail="AI任务不存在")

    ai_task.ai_response = json.dumps(req.ai_response, ensure_ascii=False)
    ai_task.status = "completed"

    # Load documents and templates
    docs = db.query(Document).filter(Document.id.in_(req.doc_ids)).all()
    templates = db.query(DocumentTemplate).filter(
        DocumentTemplate.id.in_(req.template_ids)
    ).all()

    if not docs or not templates:
        db.commit()
        return ApiResponse(data={"message": "AI response saved, no documents to re-render"})

    # Build context from first document's project
    project = db.query(Project).get(docs[0].project_id) if docs else None
    base_context = {
        "project_name": project.name if project else "",
        "product_info": project.product_info if project else "",
        "version_info": project.version_info if project else "",
        "project_description": project.description if project else "",
    }

    field_values = {
        "project_name": base_context["project_name"],
        "product_info": base_context["product_info"],
        "version_info": base_context["version_info"],
    }

    # Build re-render pairs
    doc_template_pairs = []
    for i, doc in enumerate(docs):
        tmpl = templates[min(i, len(templates) - 1)]
        doc_template_pairs.append({
            "doc_id": doc.id,
            "doc_path": doc.file_path,
            "template_id": tmpl.id,
            "template_path": tmpl.file_path,
            "doc_type": tmpl.doc_type,
        })

    results = docx_gen.re_render_documents(
        doc_template_pairs=doc_template_pairs,
        base_context=base_context,
        ai_context=req.ai_response,
        field_values=field_values,
        naming_rule=req.naming_rule or "{doc_type}",
    )

    for r in results:
        d = db.query(Document).get(r["doc_id"])
        if d:
            d.file_path = r["path"]
            d.file_name = os.path.basename(r["path"])
            d.ai_enhanced = 1
            d.status = "completed"

    db.commit()
    return ApiResponse(data={
        "message": f"Saved AI response and re-rendered {len(results)} documents",
        "re_rendered": len(results),
    })
