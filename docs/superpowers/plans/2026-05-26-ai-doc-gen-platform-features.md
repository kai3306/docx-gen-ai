# AI文档生成平台 — 功能增强实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用表单设计器替代调查表上传，增加模板组管理，支持多模板批量生成+ZIP打包，基于表单字段的文档命名规则。

**Architecture:** 新增4个数据库模型(表单模板/表单数据/模板组/文档模板)，新增5个API路由模块，新增5个前端页面，改造3个现有页面。docx_gen.py 扩展为支持多模板批量渲染和ZIP打包。

**Tech Stack:** FastAPI + SQLite + SQLAlchemy + Vue 3 + TypeScript + Ant Design Vue + docxtpl

---

### Task 1: 新增数据库模型

**Files:**
- Create: `backend/app/models/form_template.py`
- Create: `backend/app/models/form_data.py`
- Create: `backend/app/models/template_group.py`
- Create: `backend/app/models/document_template.py`
- Modify: `backend/app/models/__init__.py` (import new models)

- [ ] **Step 1: Create backend/app/models/form_template.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class FormTemplate(Base):
    __tablename__ = "form_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    fields = Column(Text, default="[]")  # JSON: [{field_key, label, type, required, options}]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

- [ ] **Step 2: Create backend/app/models/form_data.py**

```python
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
```

- [ ] **Step 3: Create backend/app/models/template_group.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class TemplateGroup(Base):
    __tablename__ = "template_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 4: Create backend/app/models/document_template.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("template_groups.id"), nullable=False)
    name = Column(String(200), nullable=False)
    doc_type = Column(String(50), default="")
    file_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 5: Update backend/app/models/__init__.py**

```python
from .user import User
from .project import Project
from .document import Document
from .ai_task import AiTask
from .form_template import FormTemplate
from .form_data import FormData
from .template_group import TemplateGroup
from .document_template import DocumentTemplate

__all__ = ["User", "Project", "Document", "AiTask", "FormTemplate", "FormData", "TemplateGroup", "DocumentTemplate"]
```

- [ ] **Step 6: Verify DB tables get created**

Run: `cd d:\Demo\Python_demo\docx-gen-ai\backend && uv run python -c "from app.database import init_db; init_db(); print('OK')"`
Expected: `OK` (tables created in app.db)

---

### Task 2: 新增 Schemas

**Files:**
- Create: `backend/app/schemas/form.py`
- Create: `backend/app/schemas/template.py`

- [ ] **Step 1: Create backend/app/schemas/form.py**

```python
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class FormFieldDef(BaseModel):
    field_key: str
    label: str
    type: str = "text"  # text, textarea, select, date
    required: bool = False
    options: list[str] = []


class FormTemplateCreate(BaseModel):
    name: str
    description: str = ""
    fields: list[FormFieldDef] = []


class FormTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[list[FormFieldDef]] = None


class FormTemplateResponse(BaseModel):
    id: int
    name: str
    description: str
    fields: Any  # list[FormFieldDef] as JSON
    created_at: datetime

    class Config:
        from_attributes = True


class FormDataCreate(BaseModel):
    form_template_id: int
    project_id: Optional[int] = None
    field_values: dict[str, Any] = {}


class FormDataUpdate(BaseModel):
    field_values: Optional[dict[str, Any]] = None


class FormDataResponse(BaseModel):
    id: int
    form_template_id: int
    project_id: Optional[int]
    field_values: Any  # dict as JSON
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 2: Create backend/app/schemas/template.py**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TemplateGroupCreate(BaseModel):
    name: str
    description: str = ""


class TemplateGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TemplateGroupResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentTemplateResponse(BaseModel):
    id: int
    group_id: int
    name: str
    doc_type: str
    file_name: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateGroupDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    templates: list[DocumentTemplateResponse] = []

    class Config:
        from_attributes = True
```

---

### Task 3: Form Template API

**Files:**
- Create: `backend/app/api/form_templates.py`

- [ ] **Step 1: Create backend/app/api/form_templates.py**

```python
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
        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "fields": json.loads(t.fields) if t.fields else [],
            "created_at": t.created_at.isoformat(),
        })
    return ApiResponse(data=result)


@router.post("", response_model=ApiResponse)
def create_form_template(req: FormTemplateCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    template = FormTemplate(
        name=req.name,
        description=req.description,
        fields=json.dumps([f.dict() for f in req.fields], ensure_ascii=False),
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
    return ApiResponse(data={
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "fields": json.loads(template.fields) if template.fields else [],
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
        template.fields = json.dumps([f.dict() for f in req.fields], ensure_ascii=False)
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
```

---

### Task 4: Form Data API

**Files:**
- Create: `backend/app/api/form_data.py`

- [ ] **Step 1: Create backend/app/api/form_data.py**

```python
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
```

---

### Task 5: Template Group API (含文件上传)

**Files:**
- Create: `backend/app/api/template_groups.py`

- [ ] **Step 1: Create backend/app/api/template_groups.py**

```python
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
    name: str = Form(...),
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
```

---

### Task 6: 修改 docx_gen.py — 支持多模板批量生成 + ZIP 打包

**Files:**
- Modify: `backend/app/services/docx_gen.py`

- [ ] **Step 1: Update docx_gen.py with batch generation and ZIP support**

```python
import os
import json
import zipfile
import io
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate
from typing import Optional

from app.core.config import settings


def _get_default_context() -> dict:
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
    }


def resolve_template_path(template_path: str) -> str:
    if os.path.isabs(template_path):
        return template_path
    template_dir = Path(settings.TEMPLATE_DIR)
    return str(template_dir / template_path)


def generate_single_document(
    template_path: str,
    context: dict,
    output_filename: str,
) -> str:
    """Generate a single Word document, return the output path."""
    full_path = resolve_template_path(template_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"模板文件不存在: {full_path}")

    doc = DocxTemplate(full_path)
    full_context = {**_get_default_context(), **context}
    doc.render(full_context)

    output_dir = Path(settings.GENERATED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = str(output_dir / output_filename)
    doc.save(output_path)
    return output_path


def resolve_naming_rule(naming_rule: str, field_values: dict) -> str:
    """Replace {field_key} placeholders with actual field values."""
    result = naming_rule
    for key, value in field_values.items():
        result = result.replace(f"{{{key}}}", str(value or ""))
    return result


def batch_generate_documents(
    templates: list[dict],
    base_context: dict,
    field_values: dict,
    naming_rule: str,
) -> bytes:
    """
    Generate multiple documents and return ZIP bytes.
    templates: [{id, name, file_path, doc_type}, ...]
    base_context: shared context (project info, ai result, etc.)
    field_values: form field values for naming
    naming_rule: e.g. "{project_name}_{doc_type}"
    """
    output_dir = Path(settings.GENERATED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for tmpl in templates:
        try:
            doc_path = tmpl["file_path"]
            if not os.path.exists(doc_path):
                continue

            doc = DocxTemplate(doc_path)
            full_context = {**_get_default_context(), **base_context}
            if "doc_type" in tmpl:
                full_context["doc_type"] = tmpl["doc_type"]
            doc.render(full_context)

            # Resolve filename from naming rule
            doc_filename = resolve_naming_rule(naming_rule, {**field_values, "doc_type": tmpl.get("doc_type", "document")})
            if not doc_filename.endswith(".docx"):
                doc_filename += ".docx"

            output_path = str(output_dir / doc_filename)
            doc.save(output_path)
            generated_files.append(output_path)
        except Exception as e:
            # Log but continue with other templates
            print(f"Template {tmpl.get('name', 'unknown')} failed: {e}")

    # If only one file, raise special signal to caller
    if len(generated_files) == 1:
        # Return the single file path
        return generated_files[0]
    elif len(generated_files) > 1:
        # Create ZIP in memory
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fp in generated_files:
                zf.write(fp, os.path.basename(fp))
        buf.seek(0)
        return buf.getvalue()

    raise ValueError("没有成功生成的文档")
```

**Key change:** The function now returns either a single file path (string) or ZIP bytes (bytes). The caller checks the type.

---

### Task 7: 修改 documents.py — 新的生成端点

**Files:**
- Modify: `backend/app/api/documents.py`

- [ ] **Step 1: Update documents.py with batch generate + ZIP download**

Replace the existing `generate_document` endpoint and add new logic:

```python
import json
import os
import io
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
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
    project_id: int
    task_id: int
    form_data_id: Optional[int] = None
    template_ids: list[int]  # DocumentTemplate IDs
    naming_rule: str = "{doc_type}"  # e.g. "{project_name}_{doc_type}"


@router.post("/generate", response_model=ApiResponse)
def batch_generate(req: BatchGenerateRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == req.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    ai_task = db.query(AiTask).filter(AiTask.id == req.task_id).first()
    if not ai_task:
        raise HTTPException(status_code=400, detail="AI任务不存在")

    ai_data = {}
    if ai_task.ai_response:
        try:
            ai_data = json.loads(ai_task.ai_response)
        except json.JSONDecodeError:
            pass

    # Get form data for naming
    field_values = {}
    if req.form_data_id:
        fd = db.query(FormData).filter(FormData.id == req.form_data_id).first()
        if fd and fd.field_values:
            try:
                field_values = json.loads(fd.field_values)
            except json.JSONDecodeError:
                pass

    # Add project info to field_values for naming
    field_values.setdefault("project_name", project.name or "")
    field_values.setdefault("product_info", project.product_info or "")
    field_values.setdefault("version_info", project.version_info or "")

    # Get selected templates
    templates = db.query(DocumentTemplate).filter(
        DocumentTemplate.id.in_(req.template_ids)
    ).all()

    if not templates:
        raise HTTPException(status_code=400, detail="未选择模板")

    # Build base context (shared across all templates)
    base_context = {
        "project_name": project.name,
        "product_info": project.product_info,
        "version_info": project.version_info,
        "project_description": project.description,
    }
    # Merge AI data (test_cases, test_results, etc.)
    base_context.update(ai_data)

    template_list = [{
        "id": t.id,
        "name": t.name,
        "file_path": t.file_path,
        "doc_type": t.doc_type,
    } for t in templates]

    try:
        # Batch generate
        naming_rule = req.naming_rule or "{doc_type}"
        result = docx_gen.batch_generate_documents(
            templates=template_list,
            base_context=base_context,
            field_values=field_values,
            naming_rule=naming_rule,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档生成失败: {str(e)}")

    # Save document records
    if isinstance(result, str):
        # Single file
        file_name = os.path.basename(result)
        doc_record = Document(
            project_id=req.project_id,
            doc_type=templates[0].doc_type or "document",
            file_name=file_name,
            file_path=result,
            status="generated",
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        return ApiResponse(data={
            "mode": "single",
            "doc_id": doc_record.id,
            "file_name": file_name,
        })
    else:
        # ZIP bytes
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"documents_{ts}.zip"
        zip_path = Path(docx_gen.settings.GENERATED_DIR) / zip_name
        with open(zip_path, "wb") as f:
            f.write(result)

        doc_record = Document(
            project_id=req.project_id,
            doc_type="batch",
            file_name=zip_name,
            file_path=str(zip_path),
            status="generated",
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        return ApiResponse(data={
            "mode": "zip",
            "doc_id": doc_record.id,
            "file_name": zip_name,
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
```

Note: Add `from datetime import datetime` at the top of the file.

- [ ] **Step 2: Add datetime import to the top of documents.py**

Add `from datetime import datetime` after `from typing import Optional`.

---

### Task 8: 更新 main.py 注册新路由

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Register new routers in main.py**

```python
from app.api import auth, projects, upload, ai, documents, form_templates, form_data, template_groups

# Add these after existing include_router lines:
app.include_router(form_templates.router, prefix="/api/form-templates", tags=["表单模板"])
app.include_router(form_data.router, prefix="/api/form-data", tags=["表单数据"])
app.include_router(template_groups.router, prefix="/api/template-groups", tags=["模板组管理"])
```

---

### Task 9: 前端 API 层

**Files:**
- Create: `frontend/src/api/formTemplate.ts`
- Create: `frontend/src/api/formData.ts`
- Create: `frontend/src/api/templateGroup.ts`

- [ ] **Step 1: Create frontend/src/api/formTemplate.ts**

```typescript
import request from './request'

export function getFormTemplates() {
  return request.get('/form-templates')
}

export function getFormTemplate(id: number) {
  return request.get(`/form-templates/${id}`)
}

export function createFormTemplate(data: {
  name: string
  description?: string
  fields: { field_key: string; label: string; type: string; required?: boolean; options?: string[] }[]
}) {
  return request.post('/form-templates', data)
}

export function updateFormTemplate(id: number, data: any) {
  return request.put(`/form-templates/${id}`, data)
}

export function deleteFormTemplate(id: number) {
  return request.delete(`/form-templates/${id}`)
}
```

- [ ] **Step 2: Create frontend/src/api/formData.ts**

```typescript
import request from './request'

export function getFormData(params?: { project_id?: number; form_template_id?: number }) {
  return request.get('/form-data', { params })
}

export function getFormDataById(id: number) {
  return request.get(`/form-data/${id}`)
}

export function createFormData(data: {
  form_template_id: number
  project_id?: number
  field_values: Record<string, any>
}) {
  return request.post('/form-data', data)
}

export function updateFormData(id: number, data: { field_values: Record<string, any> }) {
  return request.put(`/form-data/${id}`, data)
}
```

- [ ] **Step 3: Create frontend/src/api/templateGroup.ts**

```typescript
import request from './request'

export function getTemplateGroups() {
  return request.get('/template-groups')
}

export function getTemplateGroup(id: number) {
  return request.get(`/template-groups/${id}`)
}

export function createTemplateGroup(data: { name: string; description?: string }) {
  return request.post('/template-groups', data)
}

export function updateTemplateGroup(id: number, data: { name?: string; description?: string }) {
  return request.put(`/template-groups/${id}`, data)
}

export function deleteTemplateGroup(id: number) {
  return request.delete(`/template-groups/${id}`)
}

export function uploadTemplate(groupId: number, data: { name: string; doc_type?: string; file: File }) {
  const formData = new FormData()
  formData.append('name', data.name)
  if (data.doc_type) formData.append('doc_type', data.doc_type)
  formData.append('file', data.file)
  return request.post(`/template-groups/${groupId}/templates`, formData)
}

export function deleteTemplate(groupId: number, templateId: number) {
  return request.delete(`/template-groups/${groupId}/templates/${templateId}`)
}
```

---

### Task 10: 前端表单设计器页面

**Files:**
- Create: `frontend/src/views/FormTemplateList.vue`
- Create: `frontend/src/views/FormTemplateEdit.vue`

- [ ] **Step 1: Create frontend/src/views/FormTemplateList.vue**

```vue
<template>
  <div>
    <a-row justify="space-between" style="margin-bottom: 16px">
      <a-col><h2>表单模板管理</h2></a-col>
      <a-col>
        <a-button type="primary" @click="router.push('/form-templates/new')">新建表单模板</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="templates" :columns="columns" rowKey="id" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'fields'">
          {{ (record.fields || []).length }} 个字段
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="router.push(`/form-templates/edit/${record.id}`)">编辑</a>
            <a-popconfirm title="确认删除?" @confirm="handleDelete(record.id)">
              <a style="color: red">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getFormTemplates, deleteFormTemplate } from '../api/formTemplate'

const router = useRouter()
const templates = ref<any[]>([])
const loading = ref(false)

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '字段数', key: 'fields', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 150 },
]

async function load() {
  loading.value = true
  try {
    const res: any = await getFormTemplates()
    templates.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  await deleteFormTemplate(id)
  message.success('删除成功')
  load()
}

onMounted(load)
</script>
```

- [ ] **Step 2: Create frontend/src/views/FormTemplateEdit.vue**

```vue
<template>
  <div>
    <a-button style="margin-bottom: 16px" @click="router.push('/form-templates')">
      ← 返回表单模板列表
    </a-button>

    <a-card :title="isEdit ? '编辑表单模板' : '新建表单模板'">
      <a-form layout="vertical">
        <a-form-item label="模板名称" required>
          <a-input v-model:value="form.name" placeholder="例如：项目信息表单" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" rows="2" />
        </a-form-item>
      </a-form>

      <a-divider>字段定义</a-divider>

      <div v-for="(field, idx) in form.fields" :key="idx" style="border: 1px solid #d9d9d9; border-radius: 4px; padding: 16px; margin-bottom: 12px">
        <a-row :gutter="12" align="middle">
          <a-col :span="6">
            <a-form-item :label="`字段Key`">
              <a-input v-model:value="field.field_key" placeholder="例如: project_name" />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="显示名称">
              <a-input v-model:value="field.label" placeholder="例如: 项目名称" />
            </a-form-item>
          </a-col>
          <a-col :span="4">
            <a-form-item label="类型">
              <a-select v-model:value="field.type">
                <a-select-option value="text">文本</a-select-option>
                <a-select-option value="textarea">多行文本</a-select-option>
                <a-select-option value="date">日期</a-select-option>
                <a-select-option value="select">下拉选择</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="2">
            <a-form-item label="必填">
              <a-switch v-model:checked="field.required" />
            </a-form-item>
          </a-col>
          <a-col :span="4">
            <a-button danger @click="form.fields.splice(idx, 1)">删除</a-button>
          </a-col>
        </a-row>
        <a-form-item v-if="field.type === 'select'" label="选项（逗号分隔）">
          <a-input v-model:value="field.optionsText" placeholder="选项1,选项2,选项3" />
        </a-form-item>
      </div>

      <a-button type="dashed" block @click="addField" style="margin-bottom: 16px">
        + 添加字段
      </a-button>

      <a-space>
        <a-button type="primary" :loading="saving" @click="handleSave">保存</a-button>
        <a-button @click="router.push('/form-templates')">取消</a-button>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { getFormTemplate, createFormTemplate, updateFormTemplate } from '../api/formTemplate'

const router = useRouter()
const route = useRoute()
const isEdit = computed(() => route.params.id && route.params.id !== 'new')
const saving = ref(false)

const form = reactive({
  name: '',
  description: '',
  fields: [] as any[],
})

function addField() {
  form.fields.push({
    field_key: '',
    label: '',
    type: 'text',
    required: false,
    options: [],
    optionsText: '',
  })
}

async function loadTemplate() {
  if (!isEdit.value) return
  try {
    const res: any = await getFormTemplate(Number(route.params.id))
    const data = res.data
    form.name = data.name
    form.description = data.description || ''
    form.fields = (data.fields || []).map((f: any) => ({
      ...f,
      optionsText: (f.options || []).join(','),
    }))
  } catch {
    message.error('模板不存在')
    router.push('/form-templates')
  }
}

async function handleSave() {
  if (!form.name) {
    message.warning('请输入模板名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name,
      description: form.description,
      fields: form.fields.map((f: any) => ({
        field_key: f.field_key,
        label: f.label,
        type: f.type,
        required: f.required,
        options: f.optionsText ? f.optionsText.split(',').map((s: string) => s.trim()).filter(Boolean) : [],
      })),
    }
    if (isEdit.value) {
      await updateFormTemplate(Number(route.params.id), payload)
      message.success('更新成功')
    } else {
      await createFormTemplate(payload)
      message.success('创建成功')
    }
    router.push('/form-templates')
  } finally {
    saving.value = false
  }
}

onMounted(loadTemplate)
</script>
```

---

### Task 11: 前端表单填写页面

**Files:**
- Create: `frontend/src/views/FormFill.vue`

- [ ] **Step 1: Create frontend/src/views/FormFill.vue**

```vue
<template>
  <div>
    <h2>填写表单</h2>

    <a-card>
      <a-form layout="inline" style="margin-bottom: 16px">
        <a-form-item label="选择表单模板">
          <a-select v-model:value="selectedTemplateId" style="width: 250px" placeholder="选择表单模板" @change="onTemplateChange">
            <a-select-option v-for="t in formTemplates" :key="t.id" :value="t.id">{{ t.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="关联项目">
          <a-select v-model:value="selectedProjectId" style="width: 200px" placeholder="选择项目（可选）" allowClear>
            <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card v-if="fields.length > 0" title="字段填写" style="margin-top: 16px">
      <a-form layout="vertical">
        <a-form-item
          v-for="field in fields"
          :key="field.field_key"
          :label="field.label"
          :required="field.required"
        >
          <a-input
            v-if="field.type === 'text'"
            v-model:value="fieldValues[field.field_key]"
            :placeholder="`请输入${field.label}`"
          />
          <a-textarea
            v-else-if="field.type === 'textarea'"
            v-model:value="fieldValues[field.field_key]"
            :rows="3"
            :placeholder="`请输入${field.label}`"
          />
          <a-date-picker
            v-else-if="field.type === 'date'"
            v-model:value="fieldValues[field.field_key]"
            style="width: 100%"
          />
          <a-select
            v-else-if="field.type === 'select'"
            v-model:value="fieldValues[field.field_key]"
            :placeholder="`请选择${field.label}`"
            style="width: 100%"
          >
            <a-select-option v-for="opt in (field.options || [])" :key="opt" :value="opt">{{ opt }}</a-select-option>
          </a-select>
        </a-form-item>

        <a-button type="primary" :loading="saving" @click="handleSave">保存表单数据</a-button>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getFormTemplates } from '../api/formTemplate'
import { createFormData, getFormData, updateFormData } from '../api/formData'
import { getProjects } from '../api/project'

const formTemplates = ref<any[]>([])
const projects = ref<any[]>([])
const selectedTemplateId = ref<number | undefined>(undefined)
const selectedProjectId = ref<number | undefined>(undefined)
const fields = ref<any[]>([])
const fieldValues = reactive<Record<string, any>>({})
const saving = ref(false)
const existingFormDataId = ref<number | null>(null)

async function load() {
  try {
    const [ftRes, pRes]: any[] = await Promise.all([getFormTemplates(), getProjects()])
    formTemplates.value = ftRes.data || []
    projects.value = pRes.data || []
  } catch { /* ignore */ }
}

async function onTemplateChange() {
  fields.value = []
  Object.keys(fieldValues).forEach(k => delete fieldValues[k])
  existingFormDataId.value = null

  const template = formTemplates.value.find(t => t.id === selectedTemplateId.value)
  if (template) {
    fields.value = template.fields || []
  }
}

async function handleSave() {
  if (!selectedTemplateId.value) {
    message.warning('请选择表单模板')
    return
  }
  // Validate required fields
  for (const f of fields.value) {
    if (f.required && !fieldValues[f.field_key]) {
      message.warning(`请填写 ${f.label}`)
      return
    }
  }
  saving.value = true
  try {
    if (existingFormDataId.value) {
      await updateFormData(existingFormDataId.value, { field_values: { ...fieldValues } })
      message.success('更新成功')
    } else {
      await createFormData({
        form_template_id: selectedTemplateId.value,
        project_id: selectedProjectId.value,
        field_values: { ...fieldValues },
      })
      message.success('保存成功')
    }
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
```

---

### Task 12: 前端模板组管理页面

**Files:**
- Create: `frontend/src/views/TemplateGroupList.vue`
- Create: `frontend/src/views/TemplateGroupDetail.vue`

- [ ] **Step 1: Create frontend/src/views/TemplateGroupList.vue**

```vue
<template>
  <div>
    <a-row justify="space-between" style="margin-bottom: 16px">
      <a-col><h2>模板组管理</h2></a-col>
      <a-col>
        <a-button type="primary" @click="showCreate = true">新建模板组</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="groups" :columns="columns" rowKey="id" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="router.push(`/template-groups/${record.id}`)">管理模板</a>
            <a-popconfirm title="确认删除?" @confirm="handleDelete(record.id)">
              <a style="color: red">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="showCreate" title="新建模板组" @ok="handleCreate" :confirmLoading="creating">
      <a-form layout="vertical">
        <a-form-item label="名称" required>
          <a-input v-model:value="form.name" placeholder="例如：测试文档组" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getTemplateGroups, createTemplateGroup, deleteTemplateGroup } from '../api/templateGroup'

const router = useRouter()
const groups = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const form = reactive({ name: '', description: '' })

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '模板数', dataIndex: 'template_count', key: 'template_count', width: 100 },
  { title: '操作', key: 'action', width: 180 },
]

async function load() {
  loading.value = true
  try {
    const res: any = await getTemplateGroups()
    groups.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.name) { message.warning('请输入名称'); return }
  creating.value = true
  try {
    await createTemplateGroup({ ...form })
    message.success('创建成功')
    showCreate.value = false
    form.name = ''; form.description = ''
    load()
  } finally { creating.value = false }
}

async function handleDelete(id: number) {
  await deleteTemplateGroup(id)
  message.success('删除成功')
  load()
}

onMounted(load)
</script>
```

- [ ] **Step 2: Create frontend/src/views/TemplateGroupDetail.vue**

```vue
<template>
  <div>
    <a-button style="margin-bottom: 16px" @click="router.push('/template-groups')">
      ← 返回模板组列表
    </a-button>

    <a-card v-if="group" :title="group.name">
      <p>{{ group.description || '暂无描述' }}</p>
    </a-card>

    <a-card title="上传新模板" style="margin-top: 16px">
      <a-form layout="inline">
        <a-form-item label="模板名称" required>
          <a-input v-model:value="uploadForm.name" placeholder="例如：测试用例模板" />
        </a-form-item>
        <a-form-item label="文档类型">
          <a-input v-model:value="uploadForm.doc_type" placeholder="例如：test_case" />
        </a-form-item>
        <a-form-item>
        <a-upload :before-upload="handleUpload" :showUploadList="false" accept=".docx">
            <a-button type="primary" :loading="uploading">
              <UploadOutlined /> 选择 .docx 文件上传
            </a-button>
          </a-upload>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="模板列表" style="margin-top: 16px">
      <a-table :dataSource="templates" :columns="columns" rowKey="id" :loading="loading">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-popconfirm title="确认删除此模板?" @confirm="handleDeleteTemplate(record.id)">
              <a style="color: red">删除</a>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import { getTemplateGroup, uploadTemplate, deleteTemplate } from '../api/templateGroup'

const route = useRoute()
const router = useRouter()
const groupId = Number(route.params.id)
const group = ref<any>(null)
const templates = ref<any[]>([])
const loading = ref(false)
const uploading = ref(false)
const uploadForm = reactive({ name: '', doc_type: '' })

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '文档类型', dataIndex: 'doc_type', key: 'doc_type' },
  { title: '文件名', dataIndex: 'file_name', key: 'file_name' },
  { title: '操作', key: 'action', width: 100 },
]

async function load() {
  loading.value = true
  try {
    const res: any = await getTemplateGroup(groupId)
    const data = res.data
    group.value = { name: data.name, description: data.description }
    templates.value = data.templates || []
  } finally {
    loading.value = false
  }
}

async function handleUpload(file: File): Promise<boolean> {
  if (!uploadForm.name) {
    message.warning('请输入模板名称')
    return false
  }
  uploading.value = true
  try {
    await uploadTemplate(groupId, {
      name: uploadForm.name,
      doc_type: uploadForm.doc_type,
      file,
    })
    message.success('上传成功')
    uploadForm.name = ''
    uploadForm.doc_type = ''
    load()
  } finally {
    uploading.value = false
  }
  return false
}

async function handleDeleteTemplate(templateId: number) {
  await deleteTemplate(groupId, templateId)
  message.success('删除成功')
  load()
}

onMounted(load)
</script>
```

---

### Task 13: 修改现有前端页面 — Upload / AiGenerate / DocumentList + 路由

**Files:**
- Modify: `frontend/src/views/Upload.vue`
- Modify: `frontend/src/views/AiGenerate.vue`
- Modify: `frontend/src/views/DocumentList.vue`
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: Rewrite Upload.vue — 表单填写 + 功能清单上传双用途**

```vue
<template>
  <div>
    <h2>表单填写与功能清单上传</h2>

    <a-tabs v-model:activeKey="activeTab">
      <a-tab-pane key="form" tab="填写表单">
        <FormFill />
      </a-tab-pane>
      <a-tab-pane key="upload" tab="上传功能清单（供Dify AI使用）">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 16px">
            <a-form-item label="关联项目">
              <a-select v-model:value="selectedProjectId" style="width: 200px" placeholder="选择项目" allowClear>
                <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>

          <a-upload-dragger
            :before-upload="handleUpload"
            :showUploadList="false"
            accept=".docx,.xlsx,.xls,.md,.txt"
          >
            <p class="ant-upload-drag-icon"><InboxOutlined /></p>
            <p class="ant-upload-text">点击或拖拽功能清单文件</p>
            <p class="ant-upload-hint">支持 .docx / .xlsx / .md / .txt 格式</p>
          </a-upload-dragger>
        </a-card>

        <a-card v-if="uploadResult" title="上传结果" style="margin-top: 16px">
          <p>格式: {{ uploadResult.source_format }} | 内容长度: {{ uploadResult.content_length }} 字符</p>
          <a-button type="primary" @click="router.push('/ai-generate')">下一步：AI生成</a-button>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { InboxOutlined } from '@ant-design/icons-vue'
import FormFill from './FormFill.vue'
import { uploadSurvey } from '../api/upload'
import { getProjects } from '../api/project'

const router = useRouter()
const activeTab = ref('form')
const projects = ref<any[]>([])
const selectedProjectId = ref<number | undefined>(undefined)
const uploadResult = ref<any>(null)

async function loadProjects() {
  try {
    const res: any = await getProjects()
    projects.value = res.data || []
  } catch { /* ignore */ }
}

async function handleUpload(file: File): Promise<boolean> {
  try {
    const res: any = await uploadSurvey(file, selectedProjectId.value)
    uploadResult.value = res.data
    message.success('功能清单上传成功')
  } catch { /* ignore */ }
  return false
}

onMounted(loadProjects)
</script>
```

- [ ] **Step 2: Rewrite AiGenerate.vue — 模板组选择 + 命名规则配置**

```vue
<template>
  <div>
    <h2>AI生成与文档导出</h2>

    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="AI任务列表">
          <a-table :dataSource="tasks" :columns="taskColumns" rowKey="id" :loading="loading">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="record.status === 'completed' ? 'success' : 'default'">
                  {{ record.status === 'completed' ? '已完成' : record.status }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'action'">
                <a-button size="small" type="primary" :disabled="record.status !== 'completed'" @click="selectTask(record)">
                  选择
                </a-button>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>

      <a-col :span="12">
        <a-card title="生成配置">
          <template v-if="selectedTask">
            <p><strong>选中任务:</strong> #{{ selectedTask.id }}</p>
            <a-divider />

            <a-form layout="vertical">
              <a-form-item label="选择模板组">
                <a-select v-model:value="selectedGroupId" style="width: 100%" placeholder="选择模板组" @change="onGroupChange">
                  <a-select-option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</a-select-option>
                </a-select>
              </a-form-item>

              <a-form-item v-if="groupTemplates.length > 0" label="勾选要生成的模板">
                <a-checkbox-group v-model:value="selectedTemplateIds">
                  <a-checkbox v-for="t in groupTemplates" :key="t.id" :value="t.id">
                    {{ t.name }} ({{ t.doc_type }})
                  </a-checkbox>
                </a-checkbox-group>
              </a-form-item>

              <a-form-item label="选择表单数据（用于命名）">
                <a-select v-model:value="selectedFormDataId" style="width: 100%" placeholder="选择已填写的表单" allowClear>
                  <a-select-option v-for="fd in formDataList" :key="fd.id" :value="fd.id">
                    #{{ fd.id }} - {{ fd.form_template_name || '' }}
                  </a-select-option>
                </a-select>
              </a-form-item>

              <a-form-item label="文档命名规则">
                <a-input v-model:value="namingRule" placeholder="{project_name}_{doc_type}" />
                <span style="font-size: 12px; color: #888">
                  可用变量: {{ availableVars.join(', ') }}，例如: {project_name}_{doc_type}
                </span>
              </a-form-item>

              <a-button type="primary" block :loading="generating" @click="handleGenerate">
                生成文档 ({{ selectedTemplateIds.length }} 个模板)
              </a-button>
            </a-form>
          </template>
          <template v-else>
            <a-empty description="请先在左侧选择一个AI任务" />
          </template>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getAiTasks, generate } from '../api/ai'
import { getTemplateGroups, getTemplateGroup } from '../api/templateGroup'
import { getFormData } from '../api/formData'
import request from '../api/request'

const loading = ref(false)
const tasks = ref<any[]>([])
const selectedTask = ref<any>(null)
const generating = ref(false)

const groups = ref<any[]>([])
const groupTemplates = ref<any[]>([])
const selectedGroupId = ref<number | undefined>(undefined)
const selectedTemplateIds = ref<number[]>([])
const formDataList = ref<any[]>([])
const selectedFormDataId = ref<number | undefined>(undefined)
const namingRule = ref('{project_name}_{doc_type}')

const availableVars = computed(() => ['project_name', 'product_info', 'version_info', 'doc_type'])

const taskColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '格式', dataIndex: 'source_format', key: 'source_format', width: 80 },
  { title: '状态', key: 'status', width: 100 },
  { title: '时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 100 },
]

async function loadTasks() {
  loading.value = true
  try {
    const [taskRes, groupRes, fdRes]: any[] = await Promise.all([
      getAiTasks(), getTemplateGroups(), getFormData(),
    ])
    tasks.value = taskRes.data?.data || taskRes.data || []
    groups.value = groupRes.data || []
    const fdList = fdRes.data || []
    // Enrich with template names
    formDataList.value = fdList
  } finally {
    loading.value = false
  }
}

function selectTask(task: any) {
  selectedTask.value = task
  selectedTemplateIds.value = []
  groupTemplates.value = []
  selectedGroupId.value = undefined
}

async function onGroupChange() {
  if (!selectedGroupId.value) { groupTemplates.value = []; return }
  try {
    const res: any = await getTemplateGroup(selectedGroupId.value)
    groupTemplates.value = res.data?.templates || []
  } catch { groupTemplates.value = [] }
}

async function handleGenerate() {
  if (!selectedTask.value || selectedTemplateIds.value.length === 0) {
    message.warning('请选择AI任务和至少一个模板')
    return
  }
  generating.value = true
  try {
    const payload: any = {
      project_id: selectedTask.value.project_id || 0,
      task_id: selectedTask.value.id,
      template_ids: selectedTemplateIds.value,
      naming_rule: namingRule.value,
    }
    if (selectedFormDataId.value) {
      payload.form_data_id = selectedFormDataId.value
    }

    // Call AI generate first if ai_response is empty
    if (!selectedTask.value.ai_response) {
      await generate(selectedTask.value.id, selectedTask.value.task_type || 'test_case')
    }

    const res: any = await request.post('/documents/generate', payload)
    const data = res.data
    if (data?.mode === 'single') {
      // Open single doc download
      window.open(`/api/doc/${data.doc_id}`, '_blank')
      message.success('文档生成成功')
    } else if (data?.mode === 'zip') {
      window.open(`/api/doc/${data.doc_id}`, '_blank')
      message.success('ZIP打包生成成功')
    }
  } catch {
    message.error('生成失败')
  } finally {
    generating.value = false
  }
}

onMounted(loadTasks)
</script>
```

- [ ] **Step 3: Update DocumentList.vue — support ZIP type display**

In DocumentList.vue, add 'batch' to typeLabels:
```typescript
const typeLabels: Record<string, string> = {
  test_case: '测试用例',
  test_result: '执行结果',
  test_plan: '测试计划',
  test_report: '测试报告',
  record: '原始记录',
  batch: 'ZIP打包',
}
```

- [ ] **Step 4: Update router — add new routes**

```typescript
{
  path: '/form-templates',
  name: 'FormTemplateList',
  component: () => import('../views/FormTemplateList.vue'),
},
{
  path: '/form-templates/edit/:id',
  name: 'FormTemplateEdit',
  component: () => import('../views/FormTemplateEdit.vue'),
},
{
  path: '/form-fill',
  name: 'FormFill',
  component: () => import('../views/FormFill.vue'),
},
{
  path: '/template-groups',
  name: 'TemplateGroupList',
  component: () => import('../views/TemplateGroupList.vue'),
},
{
  path: '/template-groups/:id',
  name: 'TemplateGroupDetail',
  component: () => import('../views/TemplateGroupDetail.vue'),
},
```

Also update AppLayout.vue to add menu items for the new pages.

---

### Task 14: 集成测试

- [ ] **Step 1: Restart backend and frontend, run full integration test**

```bash
# Terminal 1: backend
cd d:\Demo\Python_demo\docx-gen-ai\backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: frontend
cd d:\Demo\Python_demo\docx-gen-ai\frontend
npm run dev
```

- [ ] **Step 2: API integration test flow**

Test with PowerShell:
```powershell
# Login
$login = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"testuser","password":"test123"}'
$token = $login.access_token
$headers = @{ Authorization = "Bearer $token" }

# 1. Create form template
$body = '{"name":"项目信息","fields":[{"field_key":"project_name","label":"项目名称","type":"text","required":true},{"field_key":"test_version","label":"测试版本","type":"text","required":true}]}'
Invoke-RestMethod -Uri "http://localhost:8000/api/form-templates" -Method POST -ContentType "application/json" -Headers $headers -Body $body

# 2. List form templates
Invoke-RestMethod -Uri "http://localhost:8000/api/form-templates" -Headers $headers

# 3. Create form data
$body = '{"form_template_id":1,"project_id":1,"field_values":{"project_name":"测试项目","test_version":"v1.0"}}'
Invoke-RestMethod -Uri "http://localhost:8000/api/form-data" -Method POST -ContentType "application/json" -Headers $headers -Body $body

# 4. Create template group
Invoke-RestMethod -Uri "http://localhost:8000/api/template-groups" -Method POST -ContentType "application/json" -Headers $headers -Body '{"name":"测试文档组","description":"包含测试用例和执行结果模板"}'

# 5. Upload template to group (via frontend UI)

# 6. Batch generate documents
$body = '{"project_id":1,"task_id":1,"template_ids":[1],"naming_rule":"{project_name}_{doc_type}"}'
Invoke-RestMethod -Uri "http://localhost:8000/api/documents/generate" -Method POST -ContentType "application/json" -Headers $headers -Body $body
```

- [ ] **Step 3: Frontend navigation verification**

Open http://localhost:5173, login, verify:
1. Sidebar shows new menu items: "表单模板", "模板组"
2. Form template list → create → edit fields → save
3. Upload page shows tabs: "填写表单" and "上传功能清单"
4. AI Generate page shows template group selector + naming rule config
5. Document list shows batch ZIP entries

---

## Self-Review Check

**Spec coverage:**
- 表单设计器 (spec §十一): Task 1 (model) + Task 3 (API) + Task 10 (frontend) ✓
- 表单数据填写 (spec §十一): Task 1 (model) + Task 4 (API) + Task 11 (frontend) ✓
- 模板组管理 (spec §十二): Task 1 (model) + Task 5 (API) + Task 12 (frontend) ✓
- 多文档打包 (spec §七): Task 6 (docx_gen) + Task 7 (documents API) ✓
- 文档命名规则 (spec §六): Task 6 (resolve_naming_rule) + Task 7 (naming_rule param) ✓
- 现有页面改造 (spec §十三): Task 13 ✓

**Placeholder check:** All code blocks contain complete implementation code. No TBD/TODO. ✓

**Type consistency:** `FormFieldDef.field_key`, `DocumentTemplate.file_path`, `batch_generate_documents` return type (str|bytes) consistent across all tasks. ✓
