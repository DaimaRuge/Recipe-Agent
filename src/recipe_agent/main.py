"""FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from recipe_agent import __version__
from recipe_agent.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🚀 Recipe Agent v{__version__} 启动中...")
    
    # TODO: 初始化数据库连接
    # TODO: 初始化 LLM 客户端
    # TODO: 初始化向量数据库
    
    yield
    
    # 关闭时
    print("👋 Recipe Agent 关闭中...")


app = FastAPI(
    title="Recipe Agent",
    description="个性化多模态菜谱 Agent - 智能饮食健康管理与内容创作平台",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Recipe Agent",
        "version": __version__,
        "description": "个性化多模态菜谱 Agent",
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "recipe_agent.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
