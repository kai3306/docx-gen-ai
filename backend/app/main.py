from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.api import auth, projects, upload, ai, dify, documents, form_templates, form_data, template_groups

app = FastAPI(title="AI检测文档自动生成平台", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(upload.router, prefix="/api/upload", tags=["上传"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI生成"])
app.include_router(documents.router, prefix="/api/documents", tags=["文档"])
app.include_router(documents.download_router, prefix="/api/doc", tags=["文档下载"])
app.include_router(form_templates.router, prefix="/api/form-templates", tags=["表单模板"])
app.include_router(form_data.router, prefix="/api/form-data", tags=["表单数据"])
app.include_router(template_groups.router, prefix="/api/template-groups", tags=["模板组管理"])
app.include_router(dify.router, prefix="/api/dify", tags=["Dify回调"])


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
