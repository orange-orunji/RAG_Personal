# 企业知识库智能问答系统

基于 FastAPI + LangChain + Chroma 构建的企业级 RAG 知识库系统，支持多格式文档上传、三阶混合检索、多用户认证与对话管理、热点问题缓存，并具备自动化检索质量评估体系。

## ⭐ 项目背景

为企业内部及外部人员提供制度/资源的高效检索与问答服务，解决传统文档查找耗时、信息过载的痛点。

## 🧱 技术架构

```
登录 → JWT 认证 → 用户 → HTML 前端（FastAPI 内置） → LangChain RAG 链
  ├── SQLite 用户存储
  └── 用户 ID 会话隔离
                 后端服务：
                 ├── Chroma 向量库
                 ├── HyDE 假设文档生成
                 ├── BM25 关键词索引
                 ├── BGE-Reranker 重排序
                 └── Redis 热点缓存
```

> 前端为纯 HTML/CSS/JS 单页应用，由 FastAPI 直接托管，无需额外进程。

## ✨ 核心亮点

- **多格式文档解析**：支持 PDF、Word(.docx)、Markdown、TXT 文件自动解析与向量化
- **智能检索增强**：集成 **HyDE（假设文档嵌入）**、**BGE-Reranker 重排序**、**BM25 关键词检索**，构建三阶混合检索架构
- **多轮对话记忆**：基于 LangChain `RunnableWithMessageHistory` + 自研文件持久化存储，支持会话隔离与历史回溯
- **流式响应**：服务端 SSE 推送，前端逐字打字机效果
- **多用户认证与隔离**：JWT 认证 + Cookie 持久化登录，用户数据完全物理隔离
- **Markdown 实时渲染**：流式响应支持表格、代码块、标题、列表等 Markdown 格式实时渲染
- **会话管理**：可新建、切换、重命名、删除会话，每个会话独立保持上下文
- **Redis 热点缓存**：缓存高频问题，避免重复推理，响应延迟从 23s 降至 0.01s
- **量化评估体系**：内置 Recall@K、MRR 自动化评测脚本，对比不同检索策略效果
- **纯 HTML 单页前端**：零依赖浏览器端渲染，由 FastAPI 内置托管，无需前端框架或额外进程

## 📊 检索策略对比（Top-1 召回率）

| 策略 | 纯模糊问题 (30) | 混合问题 (30模糊+13精确) |
|------|----------------|--------------------------|
| Baseline (向量) | 53.33% | 41.86% |
| HyDEOnly | 60.00% | 51.16% |
| HyDE + Rerank | **66.67%** | **48.84%** |
| HyDE + BM25 + Rerank | 50.00% | 39.53% |

> ⚡ 核心发现：HyDE+Rerank 在语义模糊场景下提升最显著。详细实验分析见 [`EVALUATION.md`](./EVALUATION.md)。

## 📂 项目结构

```
RAG_Personal/
├── main.py                         # FastAPI 入口，同时托管前端
├── app/
│   ├── api/                        # FastAPI 接口层
│   │   ├── auth.py                 # 注册/登录
│   │   ├── chat.py                 # 对话流式、历史、会话管理（含重命名）
│   │   └── document.py             # 文档上传
│   ├── static/
│   │   └── index.html              # HTML 单页前端
│   ├── services/                   # 业务逻辑层
│   │   ├── llm.py                  # RAG 链构建
│   │   ├── hyde.py                 # HyDE 检索增强
│   │   ├── bm25_service.py         # BM25 关键词索引
│   │   ├── rerank.py              # BGE-Reranker 重排序
│   │   ├── vector_store.py         # Chroma 向量库封装
│   │   ├── history_service.py      # 对话历史持久化
│   │   ├── chat.py                 # 聊天业务逻辑
│   │   ├── document.py             # 文档处理逻辑
│   │   └── KnowledgeBase_md5_service.py  # MD5 去重
│   ├── schemas/                    # Pydantic 请求/响应模型
│   ├── config/                     # 配置文件
│   ├── utils/                      # 工具模块
│   │   ├── auth.py                 # JWT 令牌、密码加密
│   │   ├── SQL_database.py         # SQLite 数据库连接
│   │   ├── redis_client.py         # Redis 客户端
│   │   └── semantic_cache.py       # 语义缓存
│   ├── eval_questions.json         # 评测问题集
│   ├── eval_retrieval.py           # 检索质量评测脚本
│   ├── redis_retrieval.py          # Redis 压测脚本
│   └── ui.py                       # Streamlit 前端界面（旧版，已由 HTML 替代）
├── download_models.py              # 下载 BGE-Reranker 模型
├── requirements.txt                # Python 依赖
└── models/                         # （需自行下载）BGE-Reranker 模型
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <你的仓库地址>
cd RAG_Personal

# 创建虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 下载模型

```bash
python download_models.py
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，并填入你的 API Key：

```bash
cp .env.example .env
```

`.env` 文件内容示例：

```ini
SILICON_API_KEY=你的API_KEY
DASHSCOPE_API_KEY=你的API_KEY
SILICON_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
SILICON_MODEL=qwen-flash
```

### 4. 启动 Redis（使用缓存功能时需要）

**Windows（Docker）**：
```bash
docker run -d -p 6379:6379 redis
```

**macOS / Linux**：
```bash
redis-server
```

### 5. 运行项目

```bash
# 一键启动（前端 + 后端同一进程，访问 http://127.0.0.1:8000）
python main.py

# 如端口被占用，指定其他端口
python -m uvicorn main:app --host 127.0.0.1 --port 9000
```

浏览器访问 `http://127.0.0.1:8000` 即可体验。

> **注意**：HTML 前端已内置于 FastAPI 中，无需额外启动 Streamlit。旧版 Streamlit 前端（`app/ui.py`）仍保留可用。

## 🔧 常见问题

| 问题 | 解决方法 |
|------|---------|
| 端口 8000 被占用 | `netstat -ano \| findstr :8000` 查看 PID，`taskkill /F /PID <号>` 释放 |
| 页面加载不出来 | 确认已执行 `pip install aiofiles`，重启后端 |
| 重命名会话失败 | 需先发送一条消息创建会话文件，或刷新页面后重试 |

# 更新日志

本文档记录企业知识库智能问答系统的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.2.0] - 2026-06-27

### 新增

- **HTML 单页前端**：纯 HTML/CSS/JS 实现，由 FastAPI 内置托管，替代 Streamlit 前端，零额外进程
- **流式 SSE 响应**：支持服务端推送 + 前端打字机效果，Markdown 实时渲染（表格、代码块、标题、列表）
- **会话管理增强**：支持新建、切换、重命名、删除会话，每个会话独立保持上下文
- **Redis 热点语义缓存**：缓存高频问题响应，延迟从 12s 降至 0.01s
- **BM25 关键词检索**：基于文档集构建关键词索引，支持与向量检索混合召回
- **MD5 文档去重**：上传文档时自动检测重复，避免相同内容重复入库

### 变更

- 前端架构从 Streamlit 迁移至 HTML 单页应用，FastAPI 直接托管静态资源
- LLM 调用改用原生 `openai` 库 `AsyncOpenAI` 客户端，支持更细粒度的流式控制
- 对话历史存储从 LangChain 默认方案替换为自研文件持久化方案（JSON 文件按用户/会话隔离）

---

## [1.1.0] - 2026-06-20

### 新增

- **HyDE 假设文档嵌入检索**：通过 LLM 生成假设文档进行向量检索，语义模糊场景下召回率提升 20%+
- **BGE-Reranker 重排序**：对检索结果进行 Cross-Encoder 重排序，进一步提升 Top-K 精准度
- **多轮对话记忆**：基于 `RunnableWithMessageHistory` 实现会话级上下文保持
- **JWT 用户认证**：注册/登录体系，Cookie 持久化，用户数据物理隔离
- **SQLite 用户存储**：用户账户与密码哈希存储
- **多格式文档解析**：支持 PDF、Word(.docx)、Markdown、TXT 自动解析与分段
- **Chroma 向量库**：本地持久化向量存储，支持文档增删

### 变更

- 项目从单脚本重构为 FastAPI + 分层架构（API / Services / Schemas / Utils）
- 引入 LangChain LCEL 链式构建 RAG 流程

---

## [1.0.0] - 2026-06-15

### 新增

- 项目初始化，基础 RAG 管线搭建
- LangChain + Chroma + DashScope Embedding 向量检索
- FastAPI 后端服务框架
- 基础文档上传与问答接口
- 检索质量评估体系：Recall@K、MRR 自动化评测脚本
- Streamlit 前端原型界面

---

## [未发布]

### 计划中

- Docker 一键部署（Dockerfile + docker-compose）
- 会话全文检索与过滤
- 文档管理增强（列表查看、删除、重向量化）
- 查询意图分类，按需启用 BM25 混合检索
- 多租户架构支持
