"""
MCP服务器API集成模块
"""
import os
import requests
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import time

from ..config import MCPServerConfig

class APIRequest(BaseModel):
    """API请求模型"""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    service: Optional[str] = None

class APIResponse(BaseModel):
    """API响应模型"""
    status_code: int
    headers: Dict[str, str]
    content: Any
    elapsed: float

class APIModule:
    """API集成模块"""
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.router = APIRouter(prefix="/api", tags=["API集成"])
        self._register_routes()
    
    def _register_routes(self):
        """注册路由"""
        @self.router.post("/request", response_model=APIResponse)
        async def make_api_request(request: APIRequest):
            """发送API请求"""
            # 设置超时
            timeout = request.timeout or self.config.api_timeout_seconds
            
            # 设置请求头
            headers = request.headers or {}
            
            # 如果指定了服务，添加API密钥
            if request.service and request.service in self.config.api_keys:
                headers["Authorization"] = f"Bearer {self.config.api_keys[request.service]}"
            
            # 准备请求参数
            kwargs = {
                "url": request.url,
                "headers": headers,
                "timeout": timeout
            }
            
            if request.params:
                kwargs["params"] = request.params
            
            if request.data:
                kwargs["json"] = request.data
            
            # 发送请求
            try:
                start_time = time.time()
                response = requests.request(request.method, **kwargs)
                elapsed = time.time() - start_time
                
                # 尝试解析JSON响应
                try:
                    content = response.json()
                except ValueError:
                    content = response.text
                
                # 返回响应
                return APIResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    content=content,
                    elapsed=elapsed
                )
            except requests.RequestException as e:
                raise HTTPException(status_code=500, detail=f"API请求失败: {str(e)}")

def create_api_module(config: MCPServerConfig) -> APIModule:
    """创建API集成模块"""
    return APIModule(config)
