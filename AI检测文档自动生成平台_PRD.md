# AI检测文档自动生成平台 PRD

## 一、项目定位

本系统是一个“AI驱动的检测文档自动生成平台”，用于自动生成以下文档：

- 测试计划
- 测试报告
- 原始记录
- 测试用例
- 测试用例执行结果

### ⚠️ 重要说明

本系统不是测试管理系统，不负责：

- 测试执行
- 缺陷管理
- 自动化测试
- 测试流程管理

仅用于：

> 检测文档自动生成与归档

---

## 二、核心数据来源

系统分为两条数据来源链路：

### 1. 功能清单文档（AI生成链路）

用于生成：

- 测试用例
- 测试用例执行结果

来源：

- Word
- Excel
- Markdown
- txt
- 需求文档

流程：

用户上传功能清单
→ 文档解析
→ Dify工作流
→ 返回JSON
→ docxtpl生成Word

---

### 2. 宜搭业务数据（结构化链路）

用于生成：

- 测试计划
- 测试报告
- 原始记录
- 项目信息
- 产品信息
- 版本信息

流程：

宜搭数据同步
→ 本地数据库
→ JSON组装
→ docxtpl生成Word

---

## 三、系统架构

                ┌──────────────┐
                │   Vue3前端   │
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │  FastAPI后端 │
                └──────┬───────┘
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   PostgreSQL      Dify API      docxtpl
        ↓
   Windows共享文件夹（存储）

---

## 四、关键设计原则

### 1. AI只负责生成JSON

禁止AI直接生成Word或长文本。

标准输出：

{
  "test_cases": [
    {
      "title": "正常登录",
      "steps": [
        "打开登录页",
        "输入账号密码",
        "点击登录"
      ],
      "expected": "登录成功"
    }
  ]
}

---

### 2. 不做强Schema校验

系统原则：

只要求合法 JSON，不限制字段结构

原因：

- Word模板会变化
- 字段会扩展
- AI输出会变化
- 保持最大灵活性

---

### 3. Word模板完全解耦

模板只负责展示，数据来自 JSON。

示例：

{{ project_name }}
{{ customer }}

{% for item in test_cases %}
{{ item.title }}
{% endfor %}

---

### 4. Dify继续作为AI执行引擎

职责：

- 功能清单 → 测试用例
- 功能清单 → 执行结果

系统只负责调用与自动化。

---

## 五、文件存储方案（Windows共享文件夹）

\192.168.1.10\test_documents

挂载后：

/mnt/shared_docs

目录结构：

shared_docs/
├── templates/
├── generated/
├── archive/
└── temp/

---

## 六、核心功能模块

### 1. 项目管理

- 同步宜搭数据
- 项目列表

---

### 2. 功能清单上传

上传 → 文本解析 → Dify → JSON

---

### 3. AI生成模块

测试用例 / 执行结果生成

---

### 4. 文档生成

JSON → docxtpl → Word

---

### 5. 历史管理

记录生成文件与版本

---

## 七、数据库设计

projects
templates
documents
ai_tasks

---

## 八、API设计

POST /api/upload/function-list
POST /api/ai/test-cases
POST /api/doc/generate
GET  /api/doc/{id}

---

## 九、技术栈

FastAPI
Vue3
PostgreSQL
Redis
Dify
docxtpl

---

## 十、开发阶段

MVP：
- 登录
- 项目
- 上传
- AI生成
- Word导出

