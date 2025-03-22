"""
通义千问(Qwen)调用MCP服务器的客户端示例
"""
import requests
import json
import os
from typing import Dict, Any, List, Optional

class QwenMCPClient:
    """通义千问(Qwen)调用MCP服务器的客户端"""
    
    def __init__(self, mcp_server_url: str, api_key: Optional[str] = None):
        """
        初始化客户端
        
        参数:
            mcp_server_url: MCP服务器URL，例如 "http://localhost:8000"
            api_key: MCP服务器API密钥（如果启用了API密钥验证）
        """
        self.mcp_server_url = mcp_server_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        
        if api_key:
            self.headers["x-api-key"] = api_key
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        上传文件到MCP服务器
        
        参数:
            file_path: 本地文件路径
            
        返回:
            文件信息
        """
        url = f"{self.mcp_server_url}/files/upload"
        
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = requests.post(url, files=files, headers={"x-api-key": self.api_key} if self.api_key else {})
        
        if response.status_code != 200:
            raise Exception(f"上传文件失败: {response.text}")
        
        return response.json()
    
    def store_vector(self, collection: str, vector: List[float], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        存储向量到MCP服务器
        
        参数:
            collection: 向量集合名称
            vector: 向量数据
            metadata: 向量元数据
            
        返回:
            向量记录信息
        """
        url = f"{self.mcp_server_url}/vector/insert"
        
        data = {
            "collection": collection,
            "vector": vector,
            "metadata": metadata or {}
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"存储向量失败: {response.text}")
        
        return response.json()
    
    def search_vector(self, collection: str, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        在MCP服务器中搜索向量
        
        参数:
            collection: 向量集合名称
            vector: 查询向量
            top_k: 返回结果数量
            
        返回:
            搜索结果列表
        """
        url = f"{self.mcp_server_url}/vector/search"
        
        data = {
            "collection": collection,
            "vector": vector,
            "top_k": top_k
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"搜索向量失败: {response.text}")
        
        return response.json()
    
    def store_document(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        存储文档到MCP服务器数据库
        
        参数:
            collection: 集合名称
            data: 文档数据
            
        返回:
            文档记录信息
        """
        url = f"{self.mcp_server_url}/database/insert"
        
        data = {
            "collection": collection,
            "data": data
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"存储文档失败: {response.text}")
        
        return response.json()
    
    def find_documents(self, collection: str, query: Dict[str, Any] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        在MCP服务器数据库中查找文档
        
        参数:
            collection: 集合名称
            query: 查询条件
            limit: 返回结果数量限制
            
        返回:
            文档列表
        """
        url = f"{self.mcp_server_url}/database/find/{collection}"
        
        params = {
            "limit": limit
        }
        
        if query:
            params["query"] = json.dumps(query)
        
        response = requests.get(url, params=params, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"查找文档失败: {response.text}")
        
        return response.json()
    
    def call_api(self, url: str, method: str = "GET", headers: Dict[str, str] = None, 
                 params: Dict[str, Any] = None, data: Dict[str, Any] = None, 
                 service: str = None) -> Dict[str, Any]:
        """
        通过MCP服务器调用外部API
        
        参数:
            url: 目标API URL
            method: 请求方法
            headers: 请求头
            params: 查询参数
            data: 请求数据
            service: 服务名称（用于获取API密钥）
            
        返回:
            API响应
        """
        mcp_url = f"{self.mcp_server_url}/api/request"
        
        request_data = {
            "url": url,
            "method": method
        }
        
        if headers:
            request_data["headers"] = headers
        
        if params:
            request_data["params"] = params
        
        if data:
            request_data["data"] = data
        
        if service:
            request_data["service"] = service
        
        response = requests.post(mcp_url, json=request_data, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"调用API失败: {response.text}")
        
        return response.json()
