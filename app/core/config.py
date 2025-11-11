"""
应用配置管理
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "CodeRetrievr"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # CORS配置（环境变量中应使用逗号分隔的字符串，如：http://localhost:3000,http://localhost:5173）
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """获取CORS origins列表"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else []
    
    # Milvus配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "code_snippets"
    MILVUS_DIMENSION: int = 768  # CodeBERT向量维度
    
    # 代码嵌入配置
    EMBEDDING_MODEL: str = "microsoft/codebert-base"  # CodeBERT模型
    EMBEDDING_DEVICE: str = "cuda"  # cpu 或 cuda（自动检测，如果CUDA不可用会回退到CPU）
    
    # Pinecone配置（可选）
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""
    PINECONE_INDEX_NAME: str = ""
    
    # Neo4j配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""  # 从环境变量读取
    
    # 大模型API配置（支持OpenAI和DeepSeek）
    LLM_PROVIDER: str = "deepseek"  # openai 或 deepseek
    LLM_API_KEY: str = ""  # OpenAI或DeepSeek的API密钥
    LLM_BASE_URL: str = ""  # DeepSeek: https://api.deepseek.com, OpenAI: 留空使用默认
    LLM_MODEL: str = "deepseek-chat"  # deepseek-chat 或 gpt-3.5-turbo
    LLM_MAX_TOKENS: int = 1000
    
    # OpenAI配置（兼容旧配置，已废弃，使用LLM_*配置）
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    
    # 代码嵌入模型配置（已在上方定义，此处为冗余配置，保留以兼容旧代码）
    # EMBEDDING_MODEL: str = "microsoft/codebert-base"
    # EMBEDDING_DEVICE: str = "cuda"
    
    # GitHub配置
    GITHUB_TOKEN: str = ""
    GITHUB_RATE_LIMIT: int = 5000
    
    # 数据存储配置
    DATA_DIR: str = "./data"
    CODE_SNIPPETS_DIR: str = "./data/code_snippets"
    METADATA_DIR: str = "./data/metadata"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 部署模式
    DEPLOYMENT_MODE: str = "local"  # local 或 cloud
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

