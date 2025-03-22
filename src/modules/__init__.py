"""
MCP服务器模块初始化
"""
from ..config import MCPServerConfig
from .file_module import create_file_module
from .database_module import create_database_module
from .api_module import create_api_module
from .vector_module import create_vector_module

__all__ = ["register_modules"]

def register_modules(server):
    """注册所有功能模块到服务器"""
    # 获取服务器配置
    config = server.config
    
    # 创建并注册文件模块
    file_module = create_file_module(config)
    server.app.include_router(file_module.router)
    
    # 创建并注册数据库模块
    database_module = create_database_module(config)
    server.app.include_router(database_module.router)
    
    # 创建并注册API集成模块
    api_module = create_api_module(config)
    server.app.include_router(api_module.router)
    
    # 创建并注册向量数据库模块
    vector_module = create_vector_module(config)
    server.app.include_router(vector_module.router)
    
    return server
