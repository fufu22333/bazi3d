# Bazi3D

Bazi3D is an experimental full-stack web project that explores turning structured user input into stylized 3D character content. The project is currently in demo / development stage, with a Flask backend, a static multi-page frontend, and a growing set of automated tests.

## Project Overview

The current version focuses on a V1 exploration workflow:

- Collecting structured user input from frontend pages
- Connecting frontend requests to backend generation-related APIs
- Generating intermediate text descriptions for character / outfit concepts
- Providing basic task flow, result placeholders, and viewer page scaffolding
- Exploring gallery, profile, and work-management style page shells
- Building a foundation for future 3D generation and display integration

## Current Status

This repository is **not yet a fully polished production system**.  
At the current stage, it mainly serves as:

- a demo-oriented engineering scaffold
- a full-stack prototype for AI + 3D workflow exploration
- a public portfolio repository for ongoing iteration

Some pages, flows, and integrations are still under development or only partially connected.

## Tech Stack

- **Backend:** Python 3.11+, Flask, SQLAlchemy, PyMySQL
- **Frontend:** HTML, CSS, vanilla JavaScript
- **AI / Model integration:** DeepSeek prompt generation, Tencent Hunyuan 3D exploration, Meshy-related adapter scaffolding
- **Database:** MySQL via SQLAlchemy connection string
- **Testing:** Python `unittest`

## Repository Structure

- `backend/`: Flask app, routes, services, adapters, models, prompt generation logic
- `frontend/`: static pages and browser-side scripts
- `tests/`: backend and frontend shell-related tests
- `init_db.py`: local database initialization script
- `requirements.txt`: Python dependencies

## Local Run

### 1. Prepare Python environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
2. Configure environment variables
Copy-Item .env.example .env

Then update .env with your own local values, for example:

SQLALCHEMY_DATABASE_URI or MySQL connection fields
JWT_SECRET_KEY
optional provider keys such as DEEPSEEK_API_KEY, MESHY_API_KEY, TENCENTCLOUD_SECRET_ID, TENCENTCLOUD_SECRET_KEY
3. Initialize the database
python init_db.py
4. Start the app
python backend/app.py

Default local entry points:

Backend health check: http://127.0.0.1:5001/health
Frontend app shell: http://127.0.0.1:5001/app
Known Issues / Notes
This repository is currently in development and may contain incomplete flows or placeholder behavior.
backend/config.py includes development-oriented fallback values such as MYSQL_PASSWORD=123456 and JWT_SECRET_KEY=dev-secret-key. These are for local development only and must not be used in production.
CORS is currently configured as * for /api/*, which is convenient for development but too permissive for production deployment.
Frontend auth tokens are currently stored in localStorage, which is acceptable for prototyping but not ideal for stronger security requirements.
backend/routes/proxy.py imports requests; make sure requests is included in requirements.txt for clean environment setup.
.env, local virtual environments, IDE metadata, caches, and generated artifacts should remain untracked in public pushes.
Roadmap
Continue improving frontend page consistency and navigation flow
Strengthen the end-to-end generation pipeline from user input to result display
Improve environment separation and deployment readiness
Replace development-oriented defaults with stricter security practices
Refine gallery / work / viewer experience for better demo quality
Public Repository Notes

This is a cleaned public-facing version of the project repository.

Before pushing publicly, make sure you do not commit:

.env
local virtual environments
IDE metadata such as .idea/
cache / log / build artifacts
private planning or requirement documents

## 中文说明

### 项目简介

Bazi3D 是一个实验性的全栈 Web 项目，旨在探索如何将结构化的用户输入转化为风格化的 3D 角色内容。  
当前项目处于 Demo / 开发阶段，包含 Flask 后端、静态多页面前端，以及围绕核心接口与页面结构的基础测试。

---

### 项目概览

当前版本主要围绕一个 V1 阶段的探索性流程展开：

- 从前端页面收集结构化用户输入
- 将前端请求接入后端生成相关接口
- 生成用于角色 / 穿搭的中间文本描述（提示信息）
- 提供基础的任务流程、结果占位与预览页面结构
- 初步搭建作品展示（gallery）、个人页（profile）等页面壳
- 为后续 3D 生成与展示链路打基础

---

### 当前状态

该仓库**尚未达到完整可用的生产系统状态**。

当前阶段主要定位为：

- 一个面向 Demo 的工程原型
- 一个 AI × 3D 工作流的全栈探索项目
- 一个持续迭代中的公开作品仓库

部分页面、功能链路与模型集成仍在开发中，或尚未完全打通。

---

### 技术栈

- **后端：** Python 3.11+、Flask、SQLAlchemy、PyMySQL
- **前端：** HTML、CSS、原生 JavaScript
- **AI / 模型相关：** DeepSeek（提示生成）、腾讯混元 3D（探索中）、Meshy 接口适配（脚手架阶段）
- **数据库：** MySQL（通过 SQLAlchemy 连接）
- **测试：** Python `unittest`

---

### 项目结构

- `backend/`：Flask 应用、路由、服务层、适配器、数据模型与提示生成逻辑
- `frontend/`：静态页面与浏览器端脚本
- `tests/`：后端接口与前端页面壳相关测试
- `init_db.py`：本地数据库初始化脚本
- `requirements.txt`：Python 依赖列表

---

### 本地运行

#### 1. 创建 Python 环境

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
2. 配置环境变量
Copy-Item .env.example .env

然后根据本地环境修改 .env 文件，例如：

SQLALCHEMY_DATABASE_URI 或 MySQL 连接信息
JWT_SECRET_KEY
可选的模型服务 Key，例如：
DEEPSEEK_API_KEY
MESHY_API_KEY
TENCENTCLOUD_SECRET_ID
TENCENTCLOUD_SECRET_KEY
3. 初始化数据库
python init_db.py
4. 启动项目
python backend/app.py

默认访问入口：

后端健康检查：http://127.0.0.1:5001/health
前端入口页面：http://127.0.0.1:5001/app
已知问题 / 注意事项
当前项目仍处于开发阶段，部分功能链路尚未打通或仅为占位实现。
backend/config.py 中包含开发用默认值（如 MYSQL_PASSWORD=123456、JWT_SECRET_KEY=dev-secret-key），仅用于本地调试，不可用于生产环境。
当前 /api/* 的 CORS 配置为 *，方便开发，但在生产环境中需要收紧。
前端 token 存储在 localStorage 中，适用于原型阶段，但不符合更高安全要求。
backend/routes/proxy.py 使用了 requests，请确保已在 requirements.txt 中声明该依赖。
.env、虚拟环境、IDE 配置文件、缓存与构建产物等不应提交到公共仓库。
后续规划
优化前端页面结构与页面之间的跳转逻辑
打通从用户输入到结果展示的完整生成链路
提升部署能力与环境隔离（开发 / 生产）
替换开发阶段的默认配置，完善安全策略
优化作品展示、模型预览与整体 Demo 体验
公共仓库说明

当前仓库为整理后的公开版本。

在公开推送前，请确保不要提交以下内容：

.env 文件
本地虚拟环境
IDE 配置文件（如 .idea/）
缓存 / 日志 / 构建产物
私人需求文档或计划文档