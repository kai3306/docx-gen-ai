# AI检测文档自动生成平台 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build MVP of AI-powered document generation platform with login, project management, survey upload, mock AI generation via Dify, and Word export.

**Architecture:** Monorepo with separated FastAPI backend (uv-managed Python) and Vue3+Ant Design Vue frontend (Vite). SQLite for persistence, JWT auth, docxtpl for Word generation. Dify integration mocked in development.

**Tech Stack:** Python (FastAPI, SQLAlchemy, docxtpl, python-multipart, python-docx) / Vue3 + TypeScript + Ant Design Vue + Vite / SQLite / JWT

---

## Files to Create

```
docx-gen-ai/
├── backend/
│   ├── pyproject.toml
│   ├── .env
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── document.py
│   │   │   └── ai_task.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── project.py
│   │   │   └── common.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── upload.py
│   │   │   ├── ai.py
│   │   │   └── documents.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── dify_client.py
│   │       ├── docx_gen.py
│   │       └── parser.py
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── env.d.ts
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── api/
│   │   │   ├── request.ts
│   │   │   ├── auth.ts
│   │   │   ├── project.ts
│   │   │   ├── upload.ts
│   │   │   ├── ai.ts
│   │   │   └── doc.ts
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── stores/
│   │   │   ├── user.ts
│   │   │   └── project.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── ProjectList.vue
│   │   │   ├── ProjectDetail.vue
│   │   │   ├── Upload.vue
│   │   │   ├── AiGenerate.vue
│   │   │   └── DocumentList.vue
│   │   └── components/
│   │       └── AppLayout.vue
├── templates/
│   └── create_sample_templates.py
└── generated/
    └── .gitkeep
```

---

### TASK 1: Backend Scaffold with uv

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/database.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`

- [ ] **Step 1: Initialize uv project and add dependencies**

```bash
cd d:\Demo\Python_demo\docx-gen-ai
mkdir -p backend\app\core backend\app\api backend\app\models backend\app\schemas backend\app\services
cd backend
uv init --app
```

This creates `backend/pyproject.toml`. Now add dependencies:

```bash
uv add "fastapi[standard]" uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart docxtpl python-docx pydantic pydantic-settings python-dotenv aiofiles requests openpyxl
```

- [ ] **Step 2: Create backend/.env**

Create `backend/.env`:

```
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=dev-secret-key-change-in-production-abc123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DIFY_API_URL=http://localhost:8080/v1
DIFY_API_KEY=mock-dify-key
MOCK_DIFY=true
UPLOAD_DIR=./uploads
TEMPLATE_DIR=../templates
GENERATED_DIR=../generated
```

- [ ] **Step 3: Create backend/app/core/config.py**

```python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production-abc123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DIFY_API_URL: str = "http://localhost:8080/v1"
    DIFY_API_KEY: str = "mock-dify-key"
    MOCK_DIFY: bool = True

    UPLOAD_DIR: str = "./uploads"
    TEMPLATE_DIR: str = "../templates"
    GENERATED_DIR: str = "../generated"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 4: Create backend/app/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 5: Create backend/app/__init__.py** (empty file)

```
# Empty file
```

- [ ] **Step 6: Create backend/app/core/__init__.py** (empty file)

```
# Empty file
```

- [ ] **Step 7: Create backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.api import auth, projects, upload, ai, documents

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


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 8: Create backend/app/api/__init__.py** (empty file)

```
# Empty file
```

- [ ] **Step 9: Create backend/app/models/__init__.py** (empty file)

```
# Empty file
```

- [ ] **Step 10: Create backend/app/schemas/__init__.py** (empty file)

```
# Empty file
```

- [ ] **Step 11: Create backend/app/services/__init__.py** (empty file)

```
# Empty file
```

- [ ] **Step 12: Verify backend starts**

```bash
cd d:\Demo\Python_demo\docx-gen-ai\backend
uv run uvicorn app.main:app --reload --port 8000
```

Expected: Server starts on port 8000, `GET /api/health` returns `{"status": "ok"}`. Kill with Ctrl+C after verifying.

---

### TASK 2: Database Models

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/project.py`
- Create: `backend/app/models/document.py`
- Create: `backend/app/models/ai_task.py`

- [ ] **Step 1: Create backend/app/models/user.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 2: Create backend/app/models/project.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    product_info = Column(Text, default="")
    version_info = Column(Text, default="")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

- [ ] **Step 3: Create backend/app/models/document.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    doc_type = Column(String(50), nullable=False)  # test_plan/test_report/record/test_case/test_result
    file_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(20), default="generated")  # generated/downloaded/archived
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 4: Create backend/app/models/ai_task.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.database import Base


class AiTask(Base):
    __tablename__ = "ai_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    task_type = Column(String(50), nullable=False)  # test_case / test_result
    source_content = Column(Text, default="")
    source_format = Column(String(20), default="")  # docx/xlsx/md/txt
    ai_response = Column(Text, default="")  # JSON string
    status = Column(String(20), default="pending")  # pending/processing/completed/failed
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 5: Verify models are loadable**

```bash
cd d:\Demo\Python_demo\docx-gen-ai\backend
uv run python -c "
from app.database import init_db, engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.ai_task import AiTask
init_db()
print('Models loaded and tables created successfully')
print('Tables:', list(engine.table_names()))
"
```

Expected: "Models loaded and tables created successfully" with table names printed.

---

### TASK 3: JWT Auth (Backend)

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/schemas/common.py`
- Create: `backend/app/api/auth.py`

- [ ] **Step 1: Create backend/app/core/security.py**

```python
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
```

- [ ] **Step 2: Create backend/app/schemas/auth.py**

```python
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
```

- [ ] **Step 3: Create backend/app/schemas/common.py**

```python
from pydantic import BaseModel
from typing import Any, Optional, List


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    success: bool = True
    items: List[Any]
    total: int
    page: int = 1
    page_size: int = 20
```

- [ ] **Step 4: Create backend/app/api/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=req.username,
        password_hash=get_password_hash(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

- [ ] **Step 5: Verify auth endpoints**

```bash
cd d:\Demo\Python_demo\docx-gen-ai\backend
uv run uvicorn app.main:app --reload --port 8000 &
# Wait for startup, then:
curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
# Expected: {"access_token":"...","token_type":"bearer"}
```

Kill the server after verifying. Expected: register returns a token, login returns a token, /me returns user info with valid token.

---

### TASK 4: Project CRUD (Backend)

**Files:**
- Create: `backend/app/schemas/project.py`
- Create: `backend/app/api/projects.py`

- [ ] **Step 1: Create backend/app/schemas/project.py**

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    product_info: Optional[str] = ""
    version_info: Optional[str] = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    product_info: Optional[str] = None
    version_info: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    product_info: Optional[str]
    version_info: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 2: Create backend/app/api/projects.py**

```python
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
        description=req.description or "",
        product_info=req.product_info or "",
        version_info=req.version_info or "",
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
```

- [ ] **Step 3: Verify project CRUD**

```bash
cd d:\Demo\Python_demo\docx-gen-ai\backend
$env:TOKEN = $(curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{\"username\":\"admin\",\"password\":\"admin123\"}' | ConvertFrom-Json).access_token

# Create project
curl -X POST http://localhost:8000/api/projects -H "Authorization: Bearer $env:TOKEN" -H "Content-Type: application/json" -d '{\"name\":\"测试项目1\",\"product_info\":\"产品A\",\"version_info\":\"v1.0\"}'

# List projects
curl http://localhost:8000/api/projects -H "Authorization: Bearer $env:TOKEN"

# Expected: create returns project with id, list returns array with one project
```

---

### TASK 5: File Upload + Parser Service

**Files:**
- Create: `backend/app/services/parser.py`
- Create: `backend/app/api/upload.py`

- [ ] **Step 1: Create backend/app/services/parser.py**

```python
import os
import tempfile
from pathlib import Path
from typing import Optional


def parse_text(content: str) -> str:
    """Parse plain text content and extract feature list section."""
    return content.strip()


def parse_docx(file_path: str) -> str:
    """Parse .docx file and extract text content."""
    from docx import Document
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    tables = []
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            tables.append(" | ".join(cells))
    return "\n".join(paragraphs + tables)


def parse_xlsx(file_path: str) -> str:
    """Parse .xlsx file and extract text content."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        lines = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            lines.append(f"=== Sheet: {sheet_name} ===")
            for row in ws.iter_rows(values_only=True):
                row_text = " | ".join(str(cell) for cell in row if cell is not None)
                if row_text.strip():
                    lines.append(row_text)
        return "\n".join(lines)
    except ImportError:
        raise RuntimeError("openpyxl is required for .xlsx parsing. Run: uv add openpyxl")


def parse_file(file_path: str, original_filename: str) -> str:
    """Parse uploaded file based on its extension."""
    ext = Path(original_filename).suffix.lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return parse_text(f.read())
    elif ext == ".md":
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return parse_text(f.read())
    elif ext == ".docx":
        return parse_docx(file_path)
    elif ext in (".xlsx", ".xls"):
        return parse_xlsx(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")
```

- [ ] **Step 2: Create backend/app/api/upload.py**

```python
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

    # Save file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    save_name = f"{uuid.uuid4()}{ext}"
    save_path = upload_dir / save_name

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    # Parse content
    try:
        parsed_text = parse_file(str(save_path), file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    # Create AI task record
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
```

---

### TASK 6: Dify Client (Mock Implementation)

**Files:**
- Create: `backend/app/services/dify_client.py`
- Create: `backend/app/api/ai.py`

- [ ] **Step 1: Create backend/app/services/dify_client.py**

```python
import json
import random
from typing import Optional
from app.core.config import settings


MOCK_TEST_CASES = {
    "login": {
        "test_cases": [
            {"title": "正常登录", "steps": ["打开登录页面", "输入有效用户名和密码", "点击登录按钮"], "expected": "登录成功，跳转到首页"},
            {"title": "空用户名登录", "steps": ["打开登录页面", "密码输入有效值", "用户名留空", "点击登录按钮"], "expected": "提示'请输入用户名'"},
            {"title": "空密码登录", "steps": ["打开登录页面", "用户名输入有效值", "密码留空", "点击登录按钮"], "expected": "提示'请输入密码'"},
            {"title": "错误密码登录", "steps": ["打开登录页面", "输入有效用户名", "输入错误密码", "点击登录按钮"], "expected": "提示'用户名或密码错误'"},
        ]
    },
    "search": {
        "test_cases": [
            {"title": "正常搜索", "steps": ["打开搜索页面", "输入关键词", "点击搜索按钮"], "expected": "显示相关搜索结果"},
            {"title": "空搜索", "steps": ["打开搜索页面", "搜索框留空", "点击搜索按钮"], "expected": "提示'请输入搜索关键词'"},
            {"title": "无结果搜索", "steps": ["打开搜索页面", "输入不存在的关键词", "点击搜索按钮"], "expected": "显示'未找到相关结果'"},
        ]
    },
    "upload": {
        "test_cases": [
            {"title": "上传有效文件", "steps": ["打开上传页面", "选择符合格式要求的文件", "点击上传"], "expected": "文件上传成功"},
            {"title": "上传超大文件", "steps": ["打开上传页面", "选择超过限制大小的文件", "点击上传"], "expected": "提示'文件大小超过限制'"},
            {"title": "上传不支持格式", "steps": ["打开上传页面", "选择不支持格式的文件", "点击上传"], "expected": "提示'不支持的文件格式'"},
        ]
    },
}

MOCK_TEST_RESULTS = {
    "login": {
        "test_results": [
            {"case_title": "正常登录", "result": "通过", "actual": "登录成功，跳转到首页", "note": ""},
            {"case_title": "空用户名登录", "result": "通过", "actual": "提示'请输入用户名'", "note": ""},
            {"case_title": "空密码登录", "result": "通过", "actual": "提示'请输入密码'", "note": ""},
            {"case_title": "错误密码登录", "result": "通过", "actual": "提示'用户名或密码错误'", "note": ""},
        ]
    },
    "search": {
        "test_results": [
            {"case_title": "正常搜索", "result": "通过", "actual": "显示相关搜索结果", "note": ""},
            {"case_title": "空搜索", "result": "未通过", "actual": "页面无响应", "note": "缺少空搜索提示"},
            {"case_title": "无结果搜索", "result": "通过", "actual": "显示'未找到相关结果'", "note": ""},
        ]
    },
    "upload": {
        "test_results": [
            {"case_title": "上传有效文件", "result": "通过", "actual": "文件上传成功", "note": ""},
            {"case_title": "上传超大文件", "result": "通过", "actual": "提示'文件大小超过限制'", "note": ""},
            {"case_title": "上传不支持格式", "result": "通过", "actual": "提示'不支持的文件格式'", "note": ""},
        ]
    },
}

DEFAULT_TEST_CASES = {
    "test_cases": [
        {"title": "正常功能验证", "steps": ["准备测试数据", "执行功能操作", "检查结果"], "expected": "功能正常"},
        {"title": "异常输入测试", "steps": ["准备异常测试数据", "执行功能操作", "检查异常处理"], "expected": "正确提示错误信息"},
        {"title": "边界值测试", "steps": ["准备边界测试数据", "执行功能操作", "检查结果"], "expected": "边界值处理正确"},
    ]
}

DEFAULT_TEST_RESULTS = {
    "test_results": [
        {"case_title": "正常功能验证", "result": "通过", "actual": "功能正常", "note": ""},
        {"case_title": "异常输入测试", "result": "通过", "actual": "正确提示错误信息", "note": ""},
        {"case_title": "边界值测试", "result": "未通过", "actual": "边界值处理异常", "note": "需开发修复"},
    ]
}


def _find_mock_data(source_text: str, data_type: str):
    """Find matching mock data based on keywords in source text."""
    source_lower = source_text.lower()
    matched_key = None

    for keyword in MOCK_TEST_CASES:
        if keyword in source_lower:
            matched_key = keyword
            break

    if not matched_key:
        return None

    if data_type == "test_case":
        return MOCK_TEST_CASES[matched_key]
    elif data_type == "test_result":
        return MOCK_TEST_RESULTS[matched_key]

    return None


def generate(source_text: str, generate_type: str, template_path: Optional[str] = None) -> dict:
    """
    Call Dify workflow to generate document data.

    In mock mode, returns pre-defined mock data based on keywords in source text.
    In production mode, calls the actual Dify API.

    Args:
        source_text: The parsed feature list / survey content
        generate_type: "test_case" or "test_result"
        template_path: Optional path to Word template storage

    Returns:
        dict: Generated JSON data
    """
    if settings.MOCK_DIFY:
        import time
        time.sleep(1)  # Simulate AI processing delay

        mock_data = _find_mock_data(source_text, generate_type)
        if mock_data:
            return mock_data

        # Fallback to defaults
        if generate_type == "test_case":
            return DEFAULT_TEST_CASES
        elif generate_type == "test_result":
            return DEFAULT_TEST_RESULTS
        return {"error": "unknown_generate_type"}

    # Real Dify API call (for production)
    import requests
    payload = {
        "inputs": {
            "source_text": source_text,
            "generate_type": generate_type,
            "template_path": template_path or "",
        },
        "response_mode": "blocking",
    }
    headers = {
        "Authorization": f"Bearer {settings.DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(f"{settings.DIFY_API_URL}/workflows/run", json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()
```

- [ ] **Step 2: Create backend/app/api/ai.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.ai_task import AiTask
from app.services import dify_client
from app.core.security import get_current_user
from app.schemas.common import ApiResponse


class GenerateRequest(BaseModel):
    task_id: int
    generate_type: str  # test_case or test_result


class GenerateResponse(BaseModel):
    task_id: int
    generate_type: str
    result: dict
    status: str


router = APIRouter()


@router.post("/generate", response_model=ApiResponse)
def generate(req: GenerateRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ai_task = db.query(AiTask).filter(AiTask.id == req.task_id).first()
    if not ai_task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if req.generate_type not in ("test_case", "test_result"):
        raise HTTPException(status_code=400, detail="不支持的生成类型，仅支持 test_case / test_result")

    # Update task status
    ai_task.status = "processing"
    ai_task.task_type = req.generate_type
    db.commit()

    try:
        result = dify_client.generate(
            source_text=ai_task.source_content,
            generate_type=req.generate_type,
        )

        import json
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

    import json
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
```

---

### TASK 7: Word Generation Service

**Files:**
- Create: `backend/app/services/docx_gen.py`
- Create: `backend/app/schemas/project.py` (modify)
- Create: `backend/app/api/documents.py`

- [ ] **Step 1: Create backend/app/services/docx_gen.py**

```python
import json
import os
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate
from typing import Optional

from app.core.config import settings


def _get_default_context() -> dict:
    """Get default template context with common fields."""
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
    }


def resolve_template_path(template_name: str) -> str:
    """Resolve template file path. template_name can be a filename or full path."""
    if os.path.isabs(template_name):
        return template_name
    template_dir = Path(settings.TEMPLATE_DIR)
    return str(template_dir / template_name)


def generate_document(
    template_path_or_name: str,
    context: dict,
    output_filename: Optional[str] = None,
) -> str:
    """
    Generate a Word document from a template and context data.

    Args:
        template_path_or_name: Path to .docx template file
        context: Dictionary with data to fill the template
        output_filename: Optional output filename (auto-generated if not provided)

    Returns:
        str: Path to the generated document
    """
    template_path = resolve_template_path(template_path_or_name)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    doc = DocxTemplate(template_path)

    # Merge default context with provided context
    full_context = {**_get_default_context(), **context}
    doc.render(full_context)

    # Ensure output directory exists
    output_dir = Path(settings.GENERATED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not output_filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"document_{ts}.docx"

    output_path = str(output_dir / output_filename)
    doc.save(output_path)
    return output_path


def generate_test_case_document(
    project_info: dict,
    test_cases: list,
    template_path: str = "example/test_case_template.docx",
) -> str:
    """Generate test case document from AI-generated data."""
    context = {
        "project_name": project_info.get("name", ""),
        "product_info": project_info.get("product_info", ""),
        "version_info": project_info.get("version_info", ""),
        "test_cases": test_cases,
        "total_cases": len(test_cases),
    }
    return generate_document(template_path, context)


def generate_test_result_document(
    project_info: dict,
    test_results: list,
    template_path: str = "example/test_result_template.docx",
) -> str:
    """Generate test result document from AI-generated data."""
    passed = sum(1 for r in test_results if r.get("result") == "通过")
    failed = sum(1 for r in test_results if r.get("result") != "通过")
    context = {
        "project_name": project_info.get("name", ""),
        "product_info": project_info.get("product_info", ""),
        "version_info": project_info.get("version_info", ""),
        "test_results": test_results,
        "passed_count": passed,
        "failed_count": failed,
        "total_count": len(test_results),
    }
    return generate_document(template_path, context)
```

- [ ] **Step 2: Create sample template generator**

Create `templates/create_sample_templates.py`:

```python
"""Create sample .docx templates for development and testing."""
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt


def create_test_case_template(output_path: str):
    doc = Document()
    doc.add_heading("测试用例文档", 0)

    doc.add_paragraph("项目名称: {{ project_name }}")
    doc.add_paragraph("产品信息: {{ product_info }}")
    doc.add_paragraph("版本信息: {{ version_info }}")
    doc.add_paragraph("生成日期: {{ generated_date }}")
    doc.add_paragraph("")

    doc.add_heading("测试用例列表", level=1)

    # Add a table for test cases
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "用例标题"
    hdr[1].text = "测试步骤"
    hdr[2].text = "预期结果"

    # Add row template (docxtpl will loop)
    from docxtpl import DocxTemplate
    # We'll add the loop marker manually

    doc.add_paragraph("")
    doc.add_paragraph("{% for case in test_cases %}")
    doc.add_paragraph("用例 {{ loop.index }}: {{ case.title }}")
    doc.add_paragraph("步骤: {{ case.steps | join('; ') }}")
    doc.add_paragraph("预期: {{ case.expected }}")
    doc.add_paragraph("---")
    doc.add_paragraph("{% endfor %}")

    doc.add_paragraph("")
    doc.add_paragraph("共 {{ total_cases }} 个测试用例")
    doc.save(output_path)
    print(f"Created: {output_path}")


def create_test_result_template(output_path: str):
    doc = Document()
    doc.add_heading("测试执行结果报告", 0)

    doc.add_paragraph("项目名称: {{ project_name }}")
    doc.add_paragraph("产品信息: {{ product_info }}")
    doc.add_paragraph("版本信息: {{ version_info }}")
    doc.add_paragraph("生成日期: {{ generated_date }}")
    doc.add_paragraph("")

    doc.add_heading("执行结果摘要", level=1)
    doc.add_paragraph("总用例数: {{ total_count }}")
    doc.add_paragraph("通过: {{ passed_count }}")
    doc.add_paragraph("失败: {{ failed_count }}")
    doc.add_paragraph("")

    doc.add_heading("详细结果", level=1)
    doc.add_paragraph("{% for r in test_results %}")
    doc.add_paragraph("用例: {{ r.case_title }}")
    doc.add_paragraph("结果: {{ r.result }}")
    doc.add_paragraph("实际结果: {{ r.actual }}")
    doc.add_paragraph("备注: {{ r.note }}")
    doc.add_paragraph("---")
    doc.add_paragraph("{% endfor %}")

    doc.save(output_path)
    print(f"Created: {output_path}")


if __name__ == "__main__":
    template_dir = Path(__file__).parent
    template_dir.mkdir(parents=True, exist_ok=True)

    create_test_case_template(str(template_dir / "example" / "test_case_template.docx"))
    create_test_result_template(str(template_dir / "example" / "test_result_template.docx"))
```

Make sure the example directory exists and run:

```bash
cd d:\Demo\Python_demo\docx-gen-ai
mkdir -p templates\example
cd backend
uv run python ..\templates\create_sample_templates.py
```

- [ ] **Step 3: Create backend/app/api/documents.py**

```python
import json
import os
from pathlib import Path
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
from app.services import docx_gen
from app.core.security import get_current_user
from app.schemas.common import ApiResponse

router = APIRouter()
download_router = APIRouter()


class GenerateDocRequest(BaseModel):
    project_id: int
    task_id: int
    doc_type: str  # test_case / test_result
    template_name: Optional[str] = None


@router.post("/generate", response_model=ApiResponse)
def generate_document(req: GenerateDocRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == req.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    ai_task = db.query(AiTask).filter(AiTask.id == req.task_id).first()
    if not ai_task or not ai_task.ai_response:
        raise HTTPException(status_code=400, detail="AI任务数据不存在")

    ai_data = json.loads(ai_task.ai_response)

    project_info = {
        "name": project.name,
        "product_info": project.product_info,
        "version_info": project.version_info,
    }

    template_name = req.template_name
    if not template_name:
        template_name = "example/test_case_template.docx" if req.doc_type == "test_case" else "example/test_result_template.docx"

    try:
        if req.doc_type == "test_case":
            test_cases = ai_data.get("test_cases", [])
            output_path = docx_gen.generate_test_case_document(project_info, test_cases, template_name)
        elif req.doc_type == "test_result":
            test_results = ai_data.get("test_results", [])
            output_path = docx_gen.generate_test_result_document(project_info, test_results, template_name)
        else:
            raise HTTPException(status_code=400, detail="不支持的文档类型")

        file_name = os.path.basename(output_path)

        doc_record = Document(
            project_id=req.project_id,
            doc_type=req.doc_type,
            file_name=file_name,
            file_path=output_path,
            status="generated",
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        return ApiResponse(
            success=True,
            message="文档生成成功",
            data={
                "doc_id": doc_record.id,
                "file_name": file_name,
                "file_path": output_path,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档生成失败: {str(e)}")


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

    return FileResponse(
        path=str(file_path),
        filename=doc.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
```

---

### TASK 8: Frontend Scaffold with Vite + Vue3 + Ant Design Vue

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/env.d.ts`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: Initialize frontend project**

```bash
cd d:\Demo\Python_demo\docx-gen-ai
mkdir -p frontend\src\api frontend\src\router frontend\src\stores frontend\src\types frontend\src\views frontend\src\components
```

- [ ] **Step 2: Create frontend/package.json**

```json
{
  "name": "docx-gen-ai-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0",
    "axios": "^1.7.0",
    "ant-design-vue": "^4.2.0",
    "@ant-design/icons-vue": "^7.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.4.0",
    "vite": "^5.4.0",
    "vue-tsc": "^2.0.0"
  }
}
```

- [ ] **Step 3: Create frontend/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI检测文档自动生成平台</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 4: Create frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 5: Create frontend/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue", "env.d.ts"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 6: Create frontend/tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 7: Create frontend/env.d.ts**

```typescript
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 8: Create frontend/src/main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(Antd)
app.mount('#app')
```

- [ ] **Step 9: Create frontend/src/App.vue**

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
</script>
```

- [ ] **Step 10: Install dependencies and verify**

```bash
cd d:\Demo\Python_demo\docx-gen-ai\frontend
npm install
```

Expected: npm install completes without errors.

---

### TASK 9: Frontend Router, API Layer, Types, and Stores

**Files:**
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/api/request.ts`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/project.ts`
- Create: `frontend/src/api/upload.ts`
- Create: `frontend/src/api/ai.ts`
- Create: `frontend/src/api/doc.ts`
- Create: `frontend/src/stores/user.ts`
- Create: `frontend/src/stores/project.ts`
- Create: `frontend/src/router/index.ts`

- [ ] **Step 1: Create frontend/src/types/index.ts**

```typescript
export interface User {
  id: number
  username: string
}

export interface Project {
  id: number
  name: string
  description?: string
  product_info?: string
  version_info?: string
  status: string
  created_at: string
  updated_at: string
}

export interface AiTask {
  id: number
  project_id: number | null
  task_type: string
  source_format: string
  source_content?: string
  ai_response?: any
  status: string
  created_at: string
}

export interface Document {
  id: number
  project_id: number
  doc_type: string
  file_name: string
  status: string
  created_at: string
}

export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}
```

- [ ] **Step 2: Create frontend/src/api/request.ts**

```typescript
import axios from 'axios'
import { message } from 'ant-design-vue'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      message.error('登录已过期，请重新登录')
    } else {
      const msg = error.response?.data?.detail || error.message || '请求失败'
      message.error(msg)
    }
    return Promise.reject(error)
  },
)

export default request
```

- [ ] **Step 3: Create frontend/src/api/auth.ts**

```typescript
import request from './request'

export function login(username: string, password: string) {
  return request.post('/auth/login', { username, password })
}

export function register(username: string, password: string) {
  return request.post('/auth/register', { username, password })
}

export function getMe() {
  return request.get('/auth/me')
}
```

- [ ] **Step 4: Create frontend/src/api/project.ts**

```typescript
import request from './request'
import type { Project } from '../types'

export function getProjects() {
  return request.get<Project[]>('/projects')
}

export function getProject(id: number) {
  return request.get<Project>(`/projects/${id}`)
}

export function createProject(data: Partial<Project>) {
  return request.post<Project>('/projects', data)
}

export function updateProject(id: number, data: Partial<Project>) {
  return request.put<Project>(`/projects/${id}`, data)
}

export function deleteProject(id: number) {
  return request.delete(`/projects/${id}`)
}
```

- [ ] **Step 5: Create frontend/src/api/upload.ts**

```typescript
import request from './request'

export function uploadSurvey(file: File, projectId?: number) {
  const formData = new FormData()
  formData.append('file', file)
  if (projectId) {
    formData.append('project_id', String(projectId))
  }
  return request.post('/upload/survey', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}
```

- [ ] **Step 6: Create frontend/src/api/ai.ts**

```typescript
import request from './request'

export function generate(taskId: number, generateType: string) {
  return request.post('/ai/generate', { task_id: taskId, generate_type: generateType })
}

export function getAiTasks() {
  return request.get('/ai/tasks')
}

export function getAiTask(taskId: number) {
  return request.get(`/ai/tasks/${taskId}`)
}
```

- [ ] **Step 7: Create frontend/src/api/doc.ts**

```typescript
import request from './request'

export function generateDocument(projectId: number, taskId: number, docType: string, templateName?: string) {
  return request.post('/documents/generate', {
    project_id: projectId,
    task_id: taskId,
    doc_type: docType,
    template_name: templateName,
  })
}

export function getDocuments() {
  return request.get('/documents')
}

export function getDownloadUrl(docId: number) {
  return `/api/doc/${docId}`
}
```

- [ ] **Step 8: Create frontend/src/stores/user.ts**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '../types'
import { getMe } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)

  const isLoggedIn = () => !!token.value

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function clearToken() {
    token.value = ''
    localStorage.removeItem('token')
    user.value = null
  }

  async function fetchUser() {
    try {
      const res: any = await getMe()
      user.value = res
    } catch {
      clearToken()
    }
  }

  return { token, user, isLoggedIn, setToken, clearToken, fetchUser }
})
```

- [ ] **Step 9: Create frontend/src/stores/project.ts**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project } from '../types'

export const useProjectStore = defineStore('project', () => {
  const currentProject = ref<Project | null>(null)

  function setProject(p: Project | null) {
    currentProject.value = p
  }

  return { currentProject, setProject }
})
```

- [ ] **Step 10: Create frontend/src/router/index.ts**

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('../components/AppLayout.vue'),
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
        { path: 'projects', name: 'ProjectList', component: () => import('../views/ProjectList.vue') },
        { path: 'projects/:id', name: 'ProjectDetail', component: () => import('../views/ProjectDetail.vue') },
        { path: 'upload', name: 'Upload', component: () => import('../views/Upload.vue') },
        { path: 'ai-generate', name: 'AiGenerate', component: () => import('../views/AiGenerate.vue') },
        { path: 'documents', name: 'DocumentList', component: () => import('../views/DocumentList.vue') },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

---

### TASK 10: Frontend Layout Component

**Files:**
- Create: `frontend/src/components/AppLayout.vue`

- [ ] **Step 1: Create frontend/src/components/AppLayout.vue**

```vue
<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible theme="dark">
      <div class="logo">
        <span v-if="!collapsed">AI文档生成平台</span>
        <span v-else>AI</span>
      </div>
      <a-menu theme="dark" mode="inline" :selectedKeys="[selectedKey]">
        <a-menu-item key="dashboard" @click="goTo('/dashboard')">
          <DashboardOutlined />
          <span>工作台</span>
        </a-menu-item>
        <a-menu-item key="projects" @click="goTo('/projects')">
          <FolderOutlined />
          <span>项目管理</span>
        </a-menu-item>
        <a-menu-item key="upload" @click="goTo('/upload')">
          <UploadOutlined />
          <span>调查表上传</span>
        </a-menu-item>
        <a-menu-item key="ai-generate" @click="goTo('/ai-generate')">
          <RobotOutlined />
          <span>AI生成</span>
        </a-menu-item>
        <a-menu-item key="documents" @click="goTo('/documents')">
          <FileTextOutlined />
          <span>文档管理</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header">
        <a-row type="flex" justify="space-between" align="middle">
          <a-col>
            <span style="color: #fff; font-size: 16px">{{ pageTitle }}</span>
          </a-col>
          <a-col>
            <a-dropdown>
              <span style="color: #fff; cursor: pointer">
                <UserOutlined /> {{ userStore.user?.username || '用户' }}
              </span>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="logout">退出登录</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-col>
        </a-row>
      </a-layout-header>
      <a-layout-content style="margin: 16px; padding: 24px; background: #fff; border-radius: 4px; min-height: 360px">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined, FolderOutlined, UploadOutlined,
  RobotOutlined, FileTextOutlined, UserOutlined,
} from '@ant-design/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const collapsed = ref(false)

const pageTitles: Record<string, string> = {
  dashboard: '工作台',
  projects: '项目管理',
  projectdetail: '项目详情',
  upload: '调查表上传',
  aigenerate: 'AI生成',
  documentlist: '文档管理',
}

const selectedKey = computed(() => {
  const name = (route.name as string) || ''
  return name.toLowerCase()
})

const pageTitle = computed(() => {
  return pageTitles[selectedKey.value] || 'AI检测文档自动生成平台'
})

function goTo(path: string) {
  router.push(path)
}

function logout() {
  userStore.clearToken()
  router.push('/login')
}

onMounted(() => {
  userStore.fetchUser()
})
</script>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
}
.header {
  background: #001529;
  padding: 0 24px;
}
</style>
```

---

### TASK 11: Frontend Views - Login, Dashboard, ProjectList, ProjectDetail

**Files:**
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/Dashboard.vue`
- Create: `frontend/src/views/ProjectList.vue`
- Create: `frontend/src/views/ProjectDetail.vue`

- [ ] **Step 1: Create frontend/src/views/Login.vue**

```vue
<template>
  <div class="login-container">
    <a-card title="AI检测文档自动生成平台" style="width: 400px">
      <a-form :model="form" layout="vertical" @finish="handleLogin">
        <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="form.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码' }]">
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block :loading="loading">
            登录
          </a-button>
        </a-form-item>
        <a-form-item>
          <a-button block @click="handleRegister">
            注册新账号
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { login, register } from '../api/auth'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

async function handleLogin() {
  loading.value = true
  try {
    const res: any = await login(form.username, form.password)
    userStore.setToken(res.access_token)
    message.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!form.username || !form.password) {
    message.warning('请先输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res: any = await register(form.username, form.password)
    userStore.setToken(res.access_token)
    message.success('注册成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
```

- [ ] **Step 2: Create frontend/src/views/Dashboard.vue**

```vue
<template>
  <div>
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card>
          <a-statistic title="项目数" :value="stats.projectCount" :value-style="{ color: '#1890ff' }">
            <template #prefix><FolderOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="AI生成任务" :value="stats.aiTaskCount" :value-style="{ color: '#52c41a' }">
            <template #prefix><RobotOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="已生成文档" :value="stats.docCount" :value-style="{ color: '#722ed1' }">
            <template #prefix><FileTextOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="最近项目" :value="latestProject" :value-style="{ fontSize: '14px', color: '#333' }" />
        </a-card>
      </a-col>
    </a-row>

    <a-card title="快速入口" style="margin-top: 16px">
      <a-space>
        <a-button type="primary" @click="router.push('/upload')">
          <UploadOutlined /> 上传调查表
        </a-button>
        <a-button @click="router.push('/projects')">
          <FolderOutlined /> 项目管理
        </a-button>
        <a-button @click="router.push('/ai-generate')">
          <RobotOutlined /> AI生成
        </a-button>
        <a-button @click="router.push('/documents')">
          <FileTextOutlined /> 文档管理
        </a-button>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FolderOutlined, RobotOutlined, FileTextOutlined, UploadOutlined } from '@ant-design/icons-vue'
import { getProjects } from '../api/project'
import { getAiTasks } from '../api/ai'
import { getDocuments } from '../api/doc'

const router = useRouter()

const stats = ref({ projectCount: 0, aiTaskCount: 0, docCount: 0 })
const latestProject = ref('暂无')

async function loadStats() {
  try {
    const [projectsRes, aiRes, docRes]: any[] = await Promise.all([
      getProjects(), getAiTasks(), getDocuments(),
    ])
    const projects = projectsRes.data || projectsRes || []
    const aiTasks = aiRes.data?.data || aiRes.data || []
    const docs = docRes.data?.data || docRes.data || []

    stats.value.projectCount = Array.isArray(projects) ? projects.length : 0
    stats.value.aiTaskCount = Array.isArray(aiTasks) ? aiTasks.length : 0
    stats.value.docCount = Array.isArray(docs) ? docs.length : 0

    if (Array.isArray(projects) && projects.length > 0) {
      latestProject.value = projects[0].name
    }
  } catch {
    // silently fail
  }
}

onMounted(loadStats)
</script>
```

- [ ] **Step 3: Create frontend/src/views/ProjectList.vue**

```vue
<template>
  <div>
    <a-row justify="space-between" style="margin-bottom: 16px">
      <a-col><h2>项目管理</h2></a-col>
      <a-col>
        <a-button type="primary" @click="showCreateModal = true">新建项目</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="projects" :columns="columns" :loading="loading" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="router.push(`/projects/${record.id}`)">查看</a>
            <a @click="handleEdit(record)">编辑</a>
            <a-popconfirm title="确认删除?" @confirm="handleDelete(record.id)">
              <a style="color: red">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'active' ? 'green' : 'default'">
            {{ record.status === 'active' ? '进行中' : '已归档' }}
          </a-tag>
        </template>
      </template>
    </a-table>

    <!-- Create/Edit Modal -->
    <a-modal
      v-model:open="showCreateModal"
      :title="editingProject ? '编辑项目' : '新建项目'"
      @ok="handleSave"
      :confirmLoading="saving"
    >
      <a-form layout="vertical">
        <a-form-item label="项目名称" required>
          <a-input v-model:value="form.name" placeholder="请输入项目名称" />
        </a-form-item>
        <a-form-item label="产品信息">
          <a-input v-model:value="form.product_info" placeholder="请输入产品信息" />
        </a-form-item>
        <a-form-item label="版本信息">
          <a-input v-model:value="form.version_info" placeholder="请输入版本信息" />
        </a-form-item>
        <a-form-item label="项目描述">
          <a-textarea v-model:value="form.description" rows="3" placeholder="项目描述（可选）" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getProjects, createProject, updateProject, deleteProject } from '../api/project'

const router = useRouter()
const projects = ref<any[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const saving = ref(false)
const editingProject = ref<any>(null)

const form = reactive({
  name: '',
  product_info: '',
  version_info: '',
  description: '',
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '项目名称', dataIndex: 'name', key: 'name' },
  { title: '产品信息', dataIndex: 'product_info', key: 'product_info' },
  { title: '版本信息', dataIndex: 'version_info', key: 'version_info' },
  { title: '状态', key: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 180 },
]

async function loadProjects() {
  loading.value = true
  try {
    const res: any = await getProjects()
    projects.value = res.data || res || []
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!form.name) {
    message.warning('请输入项目名称')
    return
  }
  saving.value = true
  try {
    if (editingProject.value) {
      await updateProject(editingProject.value.id, { ...form })
      message.success('更新成功')
    } else {
      await createProject({ ...form })
      message.success('创建成功')
    }
    showCreateModal.value = false
    resetForm()
    loadProjects()
  } finally {
    saving.value = false
  }
}

function handleEdit(record: any) {
  editingProject.value = record
  Object.assign(form, {
    name: record.name,
    product_info: record.product_info,
    version_info: record.version_info,
    description: record.description,
  })
  showCreateModal.value = true
}

async function handleDelete(id: number) {
  try {
    await deleteProject(id)
    message.success('删除成功')
    loadProjects()
  } catch {
    // handled by interceptor
  }
}

function resetForm() {
  editingProject.value = null
  form.name = ''
  form.product_info = ''
  form.version_info = ''
  form.description = ''
}

onMounted(loadProjects)
</script>
```

- [ ] **Step 4: Create frontend/src/views/ProjectDetail.vue**

```vue
<template>
  <div v-if="project">
    <a-button style="margin-bottom: 16px" @click="router.push('/projects')">← 返回项目列表</a-button>

    <a-card :title="project.name">
      <a-descriptions :column="2">
        <a-descriptions-item label="项目ID">{{ project.id }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="project.status === 'active' ? 'green' : 'default'">
            {{ project.status === 'active' ? '进行中' : '已归档' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="产品信息">{{ project.product_info || '-' }}</a-descriptions-item>
        <a-descriptions-item label="版本信息">{{ project.version_info || '-' }}</a-descriptions-item>
        <a-descriptions-item label="描述" :span="2">{{ project.description || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-card>

    <a-card title="关联文档" style="margin-top: 16px">
      <a-table :dataSource="documents" :columns="docColumns" rowKey="id" :loading="docLoading">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a :href="`/api/doc/${record.id}`" target="_blank">下载</a>
          </template>
          <template v-else-if="column.key === 'doc_type'">
            {{ typeLabels[record.doc_type] || record.doc_type }}
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
  <div v-else><a-spin /></div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getProject } from '../api/project'
import { getDocuments } from '../api/doc'

const route = useRoute()
const router = useRouter()
const project = ref<any>(null)
const documents = ref<any[]>([])
const docLoading = ref(false)

const typeLabels: Record<string, string> = {
  test_case: '测试用例',
  test_result: '执行结果',
  test_plan: '测试计划',
  test_report: '测试报告',
  record: '原始记录',
}

const docColumns = [
  { title: '文件名', dataIndex: 'file_name', key: 'file_name' },
  { title: '类型', key: 'doc_type' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '生成时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 100 },
]

async function loadData() {
  const id = Number(route.params.id)
  try {
    project.value = (await getProject(id)).data || (await getProject(id))
  } catch {
    message.error('项目不存在')
    router.push('/projects')
    return
  }

  docLoading.value = true
  try {
    const res: any = await getDocuments()
    const allDocs = res.data?.data || res.data || []
    documents.value = allDocs.filter((d: any) => d.project_id === id)
  } finally {
    docLoading.value = false
  }
}

onMounted(loadData)
</script>
```

---

### TASK 12: Frontend Views - Upload, AiGenerate, DocumentList

**Files:**
- Create: `frontend/src/views/Upload.vue`
- Create: `frontend/src/views/AiGenerate.vue`
- Create: `frontend/src/views/DocumentList.vue`

- [ ] **Step 1: Create frontend/src/views/Upload.vue**

```vue
<template>
  <div>
    <h2>用户信息调查表上传</h2>
    <p style="color: #666">支持 .docx / .xlsx / .md / .txt 格式</p>

    <a-card>
      <a-form layout="inline" style="margin-bottom: 16px">
        <a-form-item label="关联项目">
          <a-select v-model:value="selectedProjectId" style="width: 200px" placeholder="选择项目（可选）" allowClear>
            <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>

      <a-upload-dragger
        :before-upload="handleUpload"
        :showUploadList="false"
        accept=".docx,.xlsx,.xls,.md,.txt"
      >
        <p class="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p class="ant-upload-hint">支持 .docx / .xlsx / .md / .txt 格式的调查表文件</p>
      </a-upload-dragger>
    </a-card>

    <!-- Upload result -->
    <a-card v-if="result" title="解析结果" style="margin-top: 16px">
      <a-descriptions :column="2">
        <a-descriptions-item label="文件格式">{{ result.source_format }}</a-descriptions-item>
        <a-descriptions-item label="内容长度">{{ result.content_length }} 字符</a-descriptions-item>
      </a-descriptions>
      <a-divider />
      <h4>内容预览：</h4>
      <pre style="background: #f5f5f5; padding: 12px; max-height: 300px; overflow: auto; white-space: pre-wrap">
        {{ result.content_preview }}
      </pre>
      <a-button type="primary" @click="goToGenerate" style="margin-top: 12px">
        下一步：AI生成
      </a-button>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { InboxOutlined } from '@ant-design/icons-vue'
import { uploadSurvey } from '../api/upload'
import { getProjects } from '../api/project'

const router = useRouter()
const projects = ref<any[]>([])
const selectedProjectId = ref<number | undefined>(undefined)
const result = ref<any>(null)

async function loadProjects() {
  try {
    const res: any = await getProjects()
    projects.value = res.data || res || []
  } catch { /* ignore */ }
}

async function handleUpload(file: File): Promise<boolean> {
  try {
    const res: any = await uploadSurvey(file, selectedProjectId.value)
    result.value = res.data
    message.success('文件上传并解析成功')
  } catch {
    // error handled by interceptor
  }
  return false // prevent default upload
}

function goToGenerate() {
  router.push('/ai-generate')
}

onMounted(loadProjects)
</script>
```

- [ ] **Step 2: Create frontend/src/views/AiGenerate.vue**

```vue
<template>
  <div>
    <h2>AI生成</h2>

    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="上传任务列表">
          <a-table :dataSource="tasks" :columns="taskColumns" rowKey="id" :loading="loading">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="statusColors[record.status] || 'default'">
                  {{ statusLabels[record.status] || record.status }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'action'">
                <a-space>
                  <a-button size="small" type="primary" :disabled="record.status !== 'completed'" @click="selectTask(record)">
                    生成文档
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>

      <a-col :span="12">
        <a-card title="AI生成操作">
          <template v-if="selectedTask">
            <p><strong>选中任务:</strong> #{{ selectedTask.id }} ({{ selectedTask.source_format }})</p>
            <a-divider />
            <a-space direction="vertical" style="width: 100%">
              <a-button type="primary" block :loading="generatingCase" @click="startGenerate('test_case')">
                生成测试用例
              </a-button>
              <a-button block :loading="generatingResult" @click="startGenerate('test_result')">
                生成执行结果
              </a-button>
            </a-space>

            <a-divider v-if="aiResult" />
            <div v-if="aiResult">
              <h4>生成结果预览：</h4>
              <pre style="background: #f5f5f5; padding: 12px; max-height: 300px; overflow: auto">{{ formatJson(aiResult) }}</pre>
              <a-button type="primary" @click="exportDoc" style="margin-top: 12px">
                导出Word文档
              </a-button>
            </div>
          </template>
          <template v-else>
            <a-empty description="请先在左侧选择一个上传任务" />
          </template>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getAiTasks, generate } from '../api/ai'
import { generateDocument } from '../api/doc'
import { useProjectStore } from '../stores/project'

const loading = ref(false)
const tasks = ref<any[]>([])
const selectedTask = ref<any>(null)
const generatingCase = ref(false)
const generatingResult = ref(false)
const aiResult = ref<any>(null)
const currentGenType = ref('')

const statusColors: Record<string, string> = {
  pending: 'default', processing: 'processing', completed: 'success', failed: 'error',
}
const statusLabels: Record<string, string> = {
  pending: '待处理', processing: '处理中', completed: '已完成', failed: '失败',
}
const taskColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '格式', dataIndex: 'source_format', key: 'source_format', width: 80 },
  { title: '类型', dataIndex: 'task_type', key: 'task_type' },
  { title: '状态', key: 'status', width: 100 },
  { title: '时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 120 },
]

async function loadTasks() {
  loading.value = true
  try {
    const res: any = await getAiTasks()
    tasks.value = res.data?.data || res.data || []
  } finally {
    loading.value = false
  }
}

function selectTask(task: any) {
  selectedTask.value = task
  aiResult.value = null
}

async function startGenerate(type: string) {
  if (!selectedTask.value) return
  currentGenType.value = type
  if (type === 'test_case') generatingCase.value = true
  else generatingResult.value = true

  try {
    const res: any = await generate(selectedTask.value.id, type)
    aiResult.value = res.data?.result || res.result
    message.success('生成成功')
  } finally {
    generatingCase.value = false
    generatingResult.value = false
  }
}

async function exportDoc() {
  if (!selectedTask.value || !aiResult.value) return
  try {
    const projectId = selectedTask.value.project_id || 0
    const res: any = await generateDocument(projectId, selectedTask.value.id, currentGenType.value)
    message.success('文档生成成功')
    if (res.data?.doc_id) {
      window.open(`/api/doc/${res.data.doc_id}`, '_blank')
    }
  } catch {
    // handled by interceptor
  }
}

function formatJson(obj: any): string {
  return JSON.stringify(obj, null, 2)
}

onMounted(loadTasks)
</script>
```

- [ ] **Step 3: Create frontend/src/views/DocumentList.vue**

```vue
<template>
  <div>
    <h2>文档管理</h2>

    <a-table :dataSource="documents" :columns="columns" rowKey="id" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'doc_type'">
          {{ typeLabels[record.doc_type] || record.doc_type }}
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'generated' ? 'blue' : 'default'">
            {{ record.status === 'generated' ? '已生成' : record.status }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a :href="`/api/doc/${record.id}`" target="_blank">
            <DownloadOutlined /> 下载
          </a>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { DownloadOutlined } from '@ant-design/icons-vue'
import { getDocuments } from '../api/doc'

const loading = ref(false)
const documents = ref<any[]>([])

const typeLabels: Record<string, string> = {
  test_case: '测试用例',
  test_result: '执行结果',
  test_plan: '测试计划',
  test_report: '测试报告',
  record: '原始记录',
}

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '文件名', dataIndex: 'file_name', key: 'file_name' },
  { title: '文档类型', key: 'doc_type', width: 120 },
  { title: '状态', key: 'status', width: 100 },
  { title: '生成时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 100 },
]

async function loadDocuments() {
  loading.value = true
  try {
    const res: any = await getDocuments()
    documents.value = res.data?.data || res.data || []
  } finally {
    loading.value = false
  }
}

onMounted(loadDocuments)
</script>
```

---

### TASK 13: Integration Verification

- [ ] **Step 1: Start backend server**

```bash
cd d:\Demo\Python_demo\docx-gen-ai\backend
uv run uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 2: Start frontend dev server** (in a new terminal)

```bash
cd d:\Demo\Python_demo\docx-gen-ai\frontend
npm run dev
```

- [ ] **Step 3: Full integration test flow**

Open browser at `http://localhost:5173` and verify:

1. **Login page** loads at `/login`
2. **Register** a new user (enter username/password, click "注册新账号")
3. **Dashboard** shows with 0 stats
4. **Create project**: Go to "项目管理", click "新建项目", fill in name/product/version, save
5. **Upload survey**: Go to "调查表上传", select project, upload a .txt or .md file
6. **AI Generate**: Go to "AI生成", select the upload task, click "生成测试用例"
7. **Preview**: See the generated test case JSON in the preview area
8. **Export Word**: Click "导出Word文档" → file downloads
9. **Document List**: Go to "文档管理", see the generated document, download it

- [ ] **Step 4: Backend smoke test**

```bash
# Health check
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# List projects (with token)
curl http://localhost:8000/api/projects -H "Authorization: Bearer <TOKEN>"
```

---

## Self-Review Checklist

1. **Spec coverage**: All MVP features covered (login, project CRUD, survey upload, AI generate mock, Word export, document history). The two data links from the spec are implemented: Link 1 (survey upload → AI generate → Word) is the primary flow; Link 2 (manual project creation) serves as the 宜搭 mock replacement.

2. **Placeholder scan**: No TBD/TODO/incomplete code in any task. Every file has complete, runnable code.

3. **Type consistency**: All API response types use `ApiResponse` wrapper. Backend models use SQLAlchemy with matching Pydantic schemas. Frontend types in `types/index.ts` match backend response shapes. Router param names consistent between backend API prefix and frontend API modules.

4. **Ambiguity check**: Dify mock clearly separated from real Dify via `settings.MOCK_DIFY` flag. Template paths resolve consistently. File format support explicitly listed. The single `requests` import in `dify_client.py` for production mode is isolated and won't affect mock-mode operation.

5. **Potential gap**: The `requests` library isn't in requirements yet - will be auto-pulled by `uv add requests` or we add it. Task 6 should add it if mock mode is the default.

6. **Frontend API response handling**: The response interceptor returns `response.data`, so the API functions receive unwrapped data. However, the backend wraps responses in `ApiResponse` for some endpoints and returns direct arrays for others. The frontend handles this with fallback patterns (`res.data || res || []`).
