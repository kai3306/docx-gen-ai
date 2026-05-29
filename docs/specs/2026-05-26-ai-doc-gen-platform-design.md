# AI检测文档自动生成平台 - 设计文档

## 一、项目定位

AI驱动的检测文档自动生成平台，自动生成测试计划、测试报告、原始记录、测试用例、执行结果等文档。不负责测试执行、缺陷管理、自动化测试和测试流程管理。

## 二、技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + TypeScript + Ant Design Vue | SPA应用 |
| 后端 | Python FastAPI | RESTful API, uv 环境管理 |
| 数据库 | SQLite (开发) / PostgreSQL (生产) | SQLAlchemy ORM |
| 缓存 | 无 (MVP阶段) | 后续可加Redis |
| AI引擎 | Dify（工作流调用外部API生成） | AI只输出JSON |
| 文档生成 | docxtpl | Word模板渲染 |
| 认证 | JWT | 用户名密码登录 |

## 三、系统架构

```
┌──────────────────────────────────────────────────────────┐
│                    Vue3 前端 (Ant Design Vue)               │
│  登录 / 项目管理 / 表单填写 / 模板组管理 / AI生成 / 文档导出 │
└──────────────────┬───────────────────────────────────────┘
                   │ HTTP REST API (JWT Auth)
┌──────────────────▼───────────────────────────────────────┐
│                     FastAPI 后端                            │
│  ┌──────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐  │
│  │ Auth │ │ 表单/模板 │ │Upload/   │ │Dify桥接+Docx     │  │
│  │      │ │ 管理CRUD  │ │Form Data │ │批量生成+ZIP打包  │  │
│  └──────┘ └──────────┘ └──────────┘ └─────────────────┘  │
└──────────────────┬───────────────────────────────────────┘
                   │
     ┌──────────────┼──────────────────┐
     ▼              ▼                  ▼
   SQLite        Dify API           docxtpl
   (开发)          │               (Word生成)
                   │ Dify工作流调用外部API
                   ▼
           外部API (AI生成服务)
```

## 四、核心流程

### 链路1: 表单填写 + 功能清单上传 → AI生成 → Word导出

```
管理员定义表单模板(字段key、label、类型)
  → 用户创建/编辑表单数据(填写字段值)
  → 用户上传功能清单文件(单独上传,给Dify用)
  → 调用Dify工作流生成测试用例/执行结果
  → 前端预览
  → 用户选择模板组 → 勾选组内模板(可多选)
  → 选择文档命名规则(从表单字段变量拼接)
  → 后端批量生成Word(docxtpl)
  → 1个模板→下载docx, 多个→下载ZIP
```

**关键设计**：表单字段的 `field_key` 直接对应 docxtpl 模板中的变量名，填表数据映射到文档零成本。

### 链路2: 项目管理

```
用户创建项目(填写产品/版本/项目信息)
  → 保存到SQLite
  → 关联表单数据和生成的文档
```

## 五、数据库设计

### users
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| username | String(50) Unique | 用户名 |
| password_hash | String(255) | bcrypt哈希 |
| created_at | DateTime | 创建时间 |

### projects
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| name | String(200) | 项目名称 |
| description | Text | 项目描述 |
| product_info | Text | 产品信息 |
| version_info | Text | 版本信息 |
| status | String(20) | 状态 (active/archived) |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### documents
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| project_id | Integer FK | 关联项目 |
| doc_type | String(50) | 文档类型 |
| file_name | String(200) | 文件名 |
| file_path | String(500) | 存储路径 |
| status | String(20) | 状态 (generated/downloaded/archived) |
| created_at | DateTime | 创建时间 |

### ai_tasks
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| project_id | Integer FK | 关联项目 |
| task_type | String(50) | 任务类型 (test_case/test_result) |
| source_content | Text | 上传的功能清单内容 |
| source_format | String(20) | 源文件格式 |
| ai_response | Text(JSON) | Dify工作流返回的JSON |
| status | String(20) | 状态 (pending/processing/completed/failed) |
| created_at | DateTime | 创建时间 |

### form_templates ★ 新增
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| name | String(200) | 表单模板名称 |
| description | Text | 描述 |
| fields | Text(JSON) | 字段定义 JSON: [{field_key, label, type, required, options}] |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

`field_key` 与 docxtpl 模板中的变量名一一对应，例如 `project_name`、`test_version`。

### form_data ★ 新增
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| form_template_id | Integer FK | 关联表单模板 |
| project_id | Integer FK | 关联项目 |
| field_values | Text(JSON) | 字段值 JSON: {field_key: value} |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### template_groups ★ 新增
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| name | String(200) | 模板组名称 |
| description | Text | 描述 |
| created_at | DateTime | 创建时间 |

### document_templates ★ 新增
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| group_id | Integer FK | 关联模板组 |
| name | String(200) | 模板名称 (显示用) |
| doc_type | String(50) | 文档类型标识 |
| file_name | String(200) | 原始文件名 |
| file_path | String(500) | 存储路径 |
| created_at | DateTime | 创建时间 |

## 六、文档命名规则

用户通过选择表单字段变量拼接文件名，格式：
```
{field_key1}_{field_key2}_{field_key3}.docx
```

示例：
- 表单定义了 `project_name`, `test_version`, `test_date` 字段
- 用户选择命名规则为 `{project_name}_{test_version}_测试用例.docx`
- 生成时系统用表单数据中的值替换变量：`智慧园区_v2.1_测试用例.docx`

生成时前端提供：
1. 从表单字段列表中勾选要拼接的变量
2. 插入分隔符（`_`、`-` 或自定义）
3. 支持自由输入固定文本
4. 实时预览最终文件名

## 七、单文档/多文档处理

| 选中模板数 | 行为 | 响应 |
|-----------|------|------|
| 1个 | 直接生成并下载 .docx | `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| 多个 | 批量生成 → ZIP 打包 → 下载 | `Content-Type: application/zip` |

ZIP 内文件名使用用户定义的命名规则，文件清单预览。

## 八、API设计

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/auth/register | 注册 | 否 |
| POST | /api/auth/login | 登录 | 否 |
| GET | /api/projects | 项目列表 | 是 |
| POST | /api/projects | 创建项目 | 是 |
| GET | /api/projects/{id} | 项目详情 | 是 |
| PUT | /api/projects/{id} | 更新项目 | 是 |
| DELETE | /api/projects/{id} | 删除项目 | 是 |

### 表单模板 API ★ 新增
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/form-templates | 表单模板列表 |
| POST | /api/form-templates | 创建表单模板 |
| GET | /api/form-templates/{id} | 表单模板详情 |
| PUT | /api/form-templates/{id} | 更新表单模板 |
| DELETE | /api/form-templates/{id} | 删除表单模板 |

### 表单数据 API ★ 新增
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/form-data?project_id= | 查询表单数据 |
| POST | /api/form-data | 创建/更新表单数据 |
| GET | /api/form-data/{id} | 表单数据详情 |

### 模板组 API ★ 新增
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/template-groups | 模板组列表 |
| POST | /api/template-groups | 创建模板组 |
| GET | /api/template-groups/{id} | 模板组详情(含模板列表) |
| PUT | /api/template-groups/{id} | 更新模板组 |
| DELETE | /api/template-groups/{id} | 删除模板组 |

### 文档模板 API ★ 新增
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/template-groups/{id}/templates | 上传模板文件(.docx) |
| DELETE | /api/template-groups/{group_id}/templates/{id} | 删除模板 |

### 上传/AI/文档 API（调整）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload/survey | 上传功能清单文件（仅用于Dify） |
| POST | /api/ai/generate | 调用Dify工作流生成文档数据 |
| POST | /api/documents/generate | 批量生成Word文档(支持多模板+命名规则) |

## 九、目录结构调整

```
docx-gen-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── upload.py
│   │   │   ├── ai.py
│   │   │   ├── documents.py
│   │   │   ├── form_templates.py    ★ 新增
│   │   │   ├── form_data.py         ★ 新增
│   │   │   └── template_groups.py   ★ 新增
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── form_template.py     ★ 新增
│   │   │   ├── form_data.py         ★ 新增
│   │   │   ├── template_group.py    ★ 新增
│   │   │   └── document_template.py ★ 新增
│   │   ├── schemas/
│   │   │   ├── form.py              ★ 新增
│   │   │   └── template.py          ★ 新增
│   │   └── services/
│   │       ├── dify_client.py
│   │       ├── docx_gen.py          ★ 修改: 支持多模板+ZIP打包
│   │       └── parser.py
│   └── .env
├── frontend/
│   └── src/
│       ├── api/
│       │   ├── formTemplate.ts      ★ 新增
│       │   ├── formData.ts          ★ 新增
│       │   └── templateGroup.ts     ★ 新增
│       ├── views/
│       │   ├── FormTemplateList.vue  ★ 新增: 表单模板管理
│       │   ├── FormTemplateEdit.vue  ★ 新增: 表单设计器
│       │   ├── FormFill.vue          ★ 新增: 表单填写
│       │   ├── TemplateGroupList.vue ★ 新增: 模板组管理
│       │   └── TemplateGroupDetail.vue ★ 新增: 模板组详情
│       ├── Login/AppLayout/Dashboard... (不变)
│       ├── Upload.vue               ★ 修改: 改为表单填写+功能清单上传
│       ├── AiGenerate.vue           ★ 修改: 适配新流程
│       └── DocumentList.vue         ★ 修改: 适配新流程
├── templates/
│   └── example/                     ★ 修改: 支持通过模板组管理上传新模板
├── generated/
└── docs/
```

## 十、页面功能清单

| 页面 | 功能 |
|------|------|
| Login | 登录/注册 |
| Dashboard | 统计概览+快速入口 |
| ProjectList | 项目CRUD |
| ProjectDetail | 项目详情+关联文档 |
| **FormTemplateList** ★ | 表单模板列表+新建/编辑/删除 |
| **FormTemplateEdit** ★ | 表单设计器(添加字段, 设置field_key/label/类型/必填) |
| **FormFill** ★ | 选择表单模板→填写字段值→保存 |
| **TemplateGroupList** ★ | 模板组列表+新建/删除 |
| **TemplateGroupDetail** ★ | 上传.docx模板文件, 编辑模板信息 |
| Upload (改造) | 项目选择 + 表单填写 + 功能清单文件上传 |
| AiGenerate (改造) | 选择AI任务 + 选模板组 + 勾选模板 + 设命名规则 + 批量生成 |
| DocumentList | 文档列表 + 下载/ZIP下载 |

## 十一、Dify 集成策略

不变。`backend/app/services/dify_client.py` 负责与Dify API交互：
- 系统将用户上传的功能清单文件内容传递给Dify
- Dify工作流调用外部API完成测试用例和测试结果的AI生成
- 返回结构化JSON结果
- 开发阶段可启用Mock模式

## 十二、Word模板管理

**新的模板管理流程**：
1. 管理员创建**模板组**（如"测试文档组"）
2. 在模板组内**上传 .docx 模板文件**（含 docxtpl 语法）
3. 设置模板名称、文档类型标识
4. 模板文件存储在 `templates/` 目录下
5. 用户生成时选择模板组和组内模板

## 十三、生成文档流程

```
用户操作:
  1. 选择项目
  2. 填写表单数据 (字段值)
  3. 上传功能清单 (给Dify, 可选)
  4. 调用Dify生成 (AI返回JSON)
  5. 选择模板组
  6. 勾选组内模板 (可多选)
  7. 设置命名规则 (选择表单字段拼接)
  8. 确认生成

后端处理:
  1. 遍历选中的模板
  2. 对每个模板: project_info + form_data + ai_result → docxtpl渲染
  3. 命名: 用表单字段值替换命名规则中的变量
  4. 如果只有1个模板 → 直接返回 .docx
  5. 如果多个模板 → 打包ZIP → 返回 .zip
```

## 十四、MVP 功能范围

1. **登录** - JWT认证，注册/登录页面
2. **项目管理** - 项目的CRUD，手动创建
3. **表单管理** - 自定义表单模板，字段定义，表单数据填写
4. **功能清单上传** - 上传文件给Dify AI使用
5. **AI生成** - 调用Dify工作流生成测试用例/执行结果
6. **模板组管理** - 模板组CRUD，上传/管理 .docx 模板文件
7. **Word导出** - 支持单文档/ZIP打包下载，支持公式字段命名
8. **文档历史** - 已生成文档的查看和管理
