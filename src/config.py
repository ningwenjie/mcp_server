"""
MCP服务器配置模块
"""
import os
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class MCPServerConfig(BaseModel):
    """MCP服务器配置类"""
    # 服务器基本配置
    host: str = "0.0.0.0"  # 监听所有网络接口，确保Docker中可访问
    port: int = 8000
    debug: bool = False
    
    # 文件访问配置
    file_storage_path: str = "/app/storage"
    allowed_extensions: List[str] = ["txt", "pdf", "doc", "docx", "csv", "json", "xml"]
    max_file_size_mb: int = 50
    
    # 数据库配置
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "mcp_server_db"
    
    # API集成配置
    api_keys: Dict[str, str] = {}
    api_timeout_seconds: int = 30
    
    # 向量数据库配置
    vector_db_path: str = "/app/vector_db"
    vector_dimension: int = 1536  # 默认向量维度
    
    # 安全配置
    api_key_required: bool = True
    allowed_origins: List[str] = ["*"]
    
    @classmethod
    def from_env(cls) -> "MCPServerConfig":
        """从环境变量加载配置"""
        config = cls()
        
        # 服务器基本配置
        if os.getenv("MCP_HOST"):
            config.host = os.getenv("MCP_HOST")
        if os.getenv("MCP_PORT"):
            config.port = int(os.getenv("MCP_PORT"))
        if os.getenv("MCP_DEBUG"):
            config.debug = os.getenv("MCP_DEBUG").lower() == "true"
        
        # 文件访问配置
        if os.getenv("MCP_FILE_STORAGE_PATH"):
            config.file_storage_path = os.getenv("MCP_FILE_STORAGE_PATH")
        if os.getenv("MCP_ALLOWED_EXTENSIONS"):
            config.allowed_extensions = os.getenv("MCP_ALLOWED_EXTENSIONS").split(",")
        if os.getenv("MCP_MAX_FILE_SIZE_MB"):
            config.max_file_size_mb = int(os.getenv("MCP_MAX_FILE_SIZE_MB"))
        
        # 数据库配置
        if os.getenv("MCP_MONGODB_URI"):
            config.mongodb_uri = os.getenv("MCP_MONGODB_URI")
        if os.getenv("MCP_MONGODB_DB_NAME"):
            config.mongodb_db_name = os.getenv("MCP_MONGODB_DB_NAME")
        
        # API集成配置
        if os.getenv("MCP_API_TIMEOUT_SECONDS"):
            config.api_timeout_seconds = int(os.getenv("MCP_API_TIMEOUT_SECONDS"))
        
        # 向量数据库配置
        if os.getenv("MCP_VECTOR_DB_PATH"):
            config.vector_db_path = os.getenv("MCP_VECTOR_DB_PATH")
        if os.getenv("MCP_VECTOR_DIMENSION"):
            config.vector_dimension = int(os.getenv("MCP_VECTOR_DIMENSION"))
        
        # 安全配置
        if os.getenv("MCP_API_KEY_REQUIRED"):
            config.api_key_required = os.getenv("MCP_API_KEY_REQUIRED").lower() == "true"
        if os.getenv("MCP_ALLOWED_ORIGINS"):
            config.allowed_origins = os.getenv("MCP_ALLOWED_ORIGINS").split(",")
        
        # API密钥配置
        api_keys_str = os.getenv("MCP_API_KEYS", "")
        if api_keys_str:
            try:
                # 格式: "service1:key1,service2:key2"
                pairs = api_keys_str.split(",")
                for pair in pairs:
                    service, key = pair.split(":")
                    config.api_keys[service.strip()] = key.strip()
            except Exception:
                pass
        
        return config
