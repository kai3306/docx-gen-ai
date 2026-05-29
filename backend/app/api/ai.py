import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ai_task import AiTask
from app.services import dify_client
from app.core.security import get_current_user
from app.schemas.common import ApiResponse


class GenerateRequest(BaseModel):
    task_id: int
    generate_type: str


router = APIRouter()


@router.post("/generate", response_model=ApiResponse)
def generate(req: GenerateRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ai_task = db.query(AiTask).filter(AiTask.id == req.task_id).first()
    if not ai_task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if req.generate_type not in ("test_case", "test_result"):
        raise HTTPException(status_code=400, detail="不支持的生成类型，仅支持 test_case / test_result")

    ai_task.status = "processing"
    ai_task.task_type = req.generate_type
    db.commit()

    try:
        result = dify_client.generate(
            source_text=ai_task.source_content,
            generate_type=req.generate_type,
        )

        ai_task.ai_response = json.dumps(result, ensure_ascii=False)
        ai_task.status = "completed"
        db.commit()
    except Exception as e:
        ai_task.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"AI生成失败: {str(e)}")

    return ApiResponse(
        success=True,
        message="生成成功",
        data={
            "task_id": ai_task.id,
            "generate_type": req.generate_type,
            "result": result,
        },
    )


@router.get("/tasks", response_model=ApiResponse)
def list_ai_tasks(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    tasks = db.query(AiTask).order_by(AiTask.created_at.desc()).limit(50).all()
    return ApiResponse(data=[{
        "id": t.id,
        "project_id": t.project_id,
        "task_type": t.task_type,
        "source_format": t.source_format,
        "status": t.status,
        "created_at": t.created_at.isoformat(),
    } for t in tasks])


@router.get("/tasks/{task_id}", response_model=ApiResponse)
def get_ai_task(task_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    task = db.query(AiTask).filter(AiTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return ApiResponse(data={
        "id": task.id,
        "project_id": task.project_id,
        "task_type": task.task_type,
        "source_content": task.source_content[:1000] if task.source_content else "",
        "source_format": task.source_format,
        "ai_response": json.loads(task.ai_response) if task.ai_response else None,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
    })
