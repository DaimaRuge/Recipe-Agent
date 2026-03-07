"""配置管理"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    app_name: str = "Recipe Agent"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # API 配置
    api_prefix: str = "/api/v1"
    
    # 数据库配置
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # LLM 配置
    llm_model: str = "deepseek-v3"
    llm_api_key: Optional[str] = None
    llm_api_base: Optional[str] = None
    
    # 向量数据库配置
    vector_db_type: str = "chroma"  # chroma / faiss
    vector_db_path: str = "./data/vectors"
    
    # 存储配置
    storage_type: str = "local"  # local / s3
    storage_path: str = "./data/storage"
    
    # 安全配置
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS 配置
    cors_origins: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
