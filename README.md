# Recipe Agent - 个性化多模态菜谱 Agent

基于多模态 LLM 的智能饮食健康管理与内容创作一体化平台。

## 项目简介

Recipe Agent 是一款基于多模态 LLM（deepseek v3.2 / seed 2.0）与本地视觉/音频能力的智能 Agent，能够从图文/视频/语音直接生成可执行菜谱、营养与中医食疗分析、特殊人群调整、视频脚本输出及外部餐饮/电商推荐。

## 核心功能

- 📝 **文本输入 → 结构化菜谱输出**
- 👤 **个性化口味画像与偏好记忆**
- 📊 **营养基础计算（卡路里/三大营养素）**
- 🍽️ **"今天吃什么"快速候选推荐**
- 🤖 **多平台 Bot（飞书/微信/钉钉）**
- 🔒 **权限与隐私策略（默认本地加密）**

## 技术栈

- **后端框架：** Python 3.10+，FastAPI
- **Agent 编排：** LangChain（Python）
- **云模型：** deepseek / seed / OpenAI
- **视觉/视频：** OpenAI Vision / DeepSeek Vision
- **向量数据库：** ChromaDB / FAISS
- **知识库：** LlamaIndex
- **DB/存储：** Postgres + Redis + S3
- **Bot 集成：** 飞书 / 微信 / 钉钉
- **部署：** Docker + GitHub Actions，K8s

## 核心模块

### LLM 集成 (`src/recipe_agent/core/llm.py`)
- 支持 DeepSeek、Seed、OpenAI 等多种 LLM
- 统一的适配器接口
- JSON 输出强制模式

### 向量数据库 (`src/recipe_agent/core/vectordb.py`)
- 基于 ChromaDB 的向量存储
- 语义搜索支持
- 食材/菜系/难度过滤

### 多模态处理 (`src/recipe_agent/core/vision.py`)
- 图片食材识别
- 视频关键帧提取
- 食物图片分析

### Bot 集成 (`src/recipe_agent/core/bot.py`)
- 飞书、微信、钉钉适配器
- 统一消息格式
- Webhook 支持

## 项目结构

```
recipe-agent/
├── src/recipe_agent/
│   ├── api/              # FastAPI 路由
│   │   ├── recipes.py    # 菜谱 API
│   │   ├── users.py      # 用户 API
│   │   └── bot.py        # Bot Webhook
│   ├── core/             # 核心模块
│   │   ├── llm.py        # LLM 适配器
│   │   ├── vectordb.py   # 向量数据库
│   │   ├── vision.py     # 视觉处理
│   │   ├── bot.py        # Bot 适配器
│   │   └── prompts.py    # Prompt 模板
│   ├── models/           # 数据模型
│   │   ├── recipe.py     # 菜谱模型
│   │   └── user.py       # 用户模型
│   ├── services/         # 业务服务
│   │   ├── recipe_generator.py      # 菜谱生成
│   │   ├── nutrition_calculator.py  # 营养计算
│   │   ├── recommendation.py        # 推荐服务
│   │   ├── recipe_store.py          # 向量存储
│   │   ├── multimodal.py            # 多模态处理
│   │   └── bot_handler.py           # Bot 处理
│   ├── main.py           # 应用入口
│   └── cli.py            # 命令行工具
├── tests/                # 测试代码
├── config/               # 配置文件
├── docs/                 # 文档
├── schemas/              # JSON Schema
├── pyproject.toml        # 项目配置
├── Dockerfile            # Docker 构建
└── Makefile              # 常用命令
```

## 快速开始

### 环境准备

1. 克隆项目
```bash
git clone https://github.com/DaimaRuge/Recipe-Agent.git
cd Recipe-Agent
```

2. 安装依赖
```bash
pip install -e ".[dev]"
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填写 API 密钥等配置
```

### 启动服务

**开发模式：**
```bash
make run
# 或
recipe-agent serve --reload
```

**生产模式：**
```bash
recipe-agent serve --host 0.0.0.0 --port 8000
```

**Docker：**
```bash
make docker-build
make docker-run
```

### API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要功能

**1. 生成菜谱**
```bash
curl -X POST http://localhost:8000/api/v1/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "番茄炒蛋"}'
```

**2. 获取推荐**
```bash
curl http://localhost:8000/api/v1/recipes/recommendations?user_id=test&count=3
```

**3. Bot Webhook**

配置飞书/微信/钉钉的 Webhook URL：
- 飞书: `http://your-domain/api/v1/bot/feishu`
- 微信: `http://your-domain/api/v1/bot/wechat`
- 钉钉: `http://your-domain/api/v1/bot/dingtalk`

## 文档

详细的产品需求文档请参考 [PRD.md](./PRD.md)。

## 路线图

### MVP（第一轮）
- 文本输入 → 结构化菜谱输出
- 个性化口味画像与偏好记忆
- 营养基础计算
- "今天吃什么"快速候选
- 飞书/微信/钉钉文本 Bot
- 权限与隐私策略

### MVP+（第二轮）
- 图片 → 菜谱
- 视频 → 菜谱
- 特殊人群规则
- 中医节气食疗规则集

### 长期（第三轮及以后）
- 餐厅对接，外部就餐推荐
- 电商对接，一键购菜
- 本地化离线模型与混合推理
- 高级菜单计划与库存管理

## 贡献指南

*待补充...*

## 许可证

*待补充...*

## 联系方式

- 作者：Agent 产品与技术大宗师
- 项目：为 DaimaRuge 优化
