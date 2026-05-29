import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ai_task import AiTask
from app.services.parser import parse_file
from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.common import ApiResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".docx", ".xlsx", ".xls", ".md", ".txt"}


@router.post("/survey", response_model=ApiResponse)
async def upload_survey(
    project_id: int = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}，仅支持 {', '.join(ALLOWED_EXTENSIONS)}")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    save_name = f"{uuid.uuid4()}{ext}"
    save_path = upload_dir / save_name

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    try:
        parsed_text = parse_file(str(save_path), file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    ai_task = AiTask(
        project_id=project_id,
        task_type="survey",
        source_content=parsed_text,
        source_format=ext.lstrip("."),
        status="completed",
    )
    db.add(ai_task)
    db.commit()
    db.refresh(ai_task)

    return ApiResponse(
        success=True,
        message="文件上传并解析成功",
        data={
            "task_id": ai_task.id,
            "content_preview": parsed_text[:500],
            "content_length": len(parsed_text),
            "source_format": ext.lstrip("."),
        },
    )
