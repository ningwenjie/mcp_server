"""
MCP服务器主应用程序
"""
import os
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from src.modules.database_module import mongo_serializer
from .config import MCPServerConfig
from .modules import register_modules
from src.modules.database_module import MongoJSONEncoder


class MCPServer:
    """MCP服务器主类"""
    def __init__(self, config: MCPServerConfig = None):
        self.config = config or MCPServerConfig.from_env()
        self.app = FastAPI(
            title="MCP服务器",
            description="多功能计算平台服务器，支持文件访问、数据库连接、API集成和向量数据库访问",
            version="1.0.0"
        )
        # 设置自定义 JSON 编码器
        self.app.json_encoder = MongoJSONEncoder
        # 配置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 初始化存储目录
        os.makedirs(self.config.file_storage_path, exist_ok=True)
        os.makedirs(self.config.vector_db_path, exist_ok=True)

        # 注册中间件
        self.app.middleware("http")(self._process_request)

        # 注册路由
        self._register_routes()

        # 注册功能模块
        register_modules(self)

    async def _process_request(self, request: Request, call_next):
        """请求处理中间件"""
        # API密钥验证
        if self.config.api_key_required and not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            api_key = request.headers.get("x-api-key")
            if not api_key:
                return HTTPException(status_code=401, detail="API密钥缺失")

            # 验证API密钥 (简单实现，实际应用中应使用更安全的方法)
            valid_key = False
            for _, key in self.config.api_keys.items():
                if api_key == key:
                    valid_key = True
                    break

            if not valid_key:
                return HTTPException(status_code=401, detail="无效的API密钥")

        # 继续处理请求
        response = await call_next(request)
        return response

    def _register_routes(self):
        """注册API路由"""
        @self.app.get("/")
        async def root():
            return {"message": "欢迎使用MCP服务器", "version": "1.0.0"}

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy"}

    def run(self):
        """运行服务器"""
        import uvicorn
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="debug" if self.config.debug else "info"
        )

# 创建默认服务器实例
def create_server(config: MCPServerConfig = None) -> MCPServer:
    """创建MCP服务器实例"""
    return MCPServer(config)
