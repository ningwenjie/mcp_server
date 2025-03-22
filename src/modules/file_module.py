"""
MCP服务器文件访问模块
"""
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Form
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from ..config import MCPServerConfig

class FileInfo(BaseModel):
    """文件信息模型"""
    id: str
    filename: str
    size: int
    content_type: str
    created_at: str
    path: str

class FileModule:
    """文件访问模块"""
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.router = APIRouter(prefix="/files", tags=["文件访问"])
        self._register_routes()

    def _register_routes(self):
        """注册路由"""
        @self.router.post("/upload", response_model=FileInfo)
        async def upload_file(file: UploadFile = File(...)):
            """上传文件"""
            # 检查文件扩展名
            ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
            if ext not in self.config.allowed_extensions:
                raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

            # 检查文件大小
            file_size = 0
            content = await file.read()
            file_size = len(content)
            await file.seek(0)  # 重置文件指针

            if file_size > self.config.max_file_size_mb * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"文件大小超过限制: {self.config.max_file_size_mb}MB")

            # 生成唯一文件ID和存储路径
            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}_{file.filename}"
            file_path = os.path.join(self.config.file_storage_path, safe_filename)

            # 保存文件
            with open(file_path, "wb") as f:
                f.write(content)

            # 返回文件信息
            return FileInfo(
                id=file_id,
                filename=file.filename,
                size=file_size,
                content_type=file.content_type or "application/octet-stream",
                created_at=datetime.now().isoformat(),
                path=file_path
            )

        @self.router.get("/list", response_model=List[FileInfo])
        async def list_files():
            """列出所有文件"""
            files = []
            for filename in os.listdir(self.config.file_storage_path):
                file_path = os.path.join(self.config.file_storage_path, filename)
                if os.path.isfile(file_path):
                    # 解析文件ID
                    file_id = filename.split("_")[0] if "_" in filename else "unknown"
                    original_filename = "_".join(filename.split("_")[1:]) if "_" in filename else filename

                    # 获取文件信息
                    file_stat = os.stat(file_path)
                    files.append(FileInfo(
                        id=file_id,
                        filename=original_filename,
                        size=file_stat.st_size,
                        content_type="application/octet-stream",  # 简化处理
                        created_at=datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        path=file_path
                    ))
            return files

        @self.router.get("/download/{file_id}")
        async def download_file(file_id: str):
            """下载文件"""
            # 查找文件
            for filename in os.listdir(self.config.file_storage_path):
                if filename.startswith(f"{file_id}_"):
                    file_path = os.path.join(self.config.file_storage_path, filename)
                    original_filename = "_".join(filename.split("_")[1:])
                    return FileResponse(
                        path=file_path,
                        filename=original_filename,
                        media_type="application/octet-stream"
                    )

            raise HTTPException(status_code=404, detail=f"文件未找到: {file_id}")

        @self.router.delete("/{file_id}")
        async def delete_file(file_id: str):
            """删除文件"""
            # 查找文件
            for filename in os.listdir(self.config.file_storage_path):
                if filename.startswith(f"{file_id}_"):
                    file_path = os.path.join(self.config.file_storage_path, filename)
                    os.remove(file_path)
                    return {"message": f"文件已删除: {file_id}"}

            raise HTTPException(status_code=404, detail=f"文件未找到: {file_id}")

def create_file_module(config: MCPServerConfig) -> FileModule:
    """创建文件访问模块"""
    return FileModule(config)
