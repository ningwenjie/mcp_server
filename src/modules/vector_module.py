"""
MCP服务器向量数据库访问模块
"""
import os
import numpy as np
import faiss
import json
import uuid
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ..config import MCPServerConfig

class VectorRecord(BaseModel):
    """向量记录模型"""
    id: Optional[str] = None
    collection: str
    vector: List[float]
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

class VectorQuery(BaseModel):
    """向量查询模型"""
    vector: List[float]
    top_k: int = 5
    collection: str

class VectorSearchResult(BaseModel):
    """向量搜索结果模型"""
    id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class VectorModule:
    """向量数据库访问模块"""
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.router = APIRouter(prefix="/vector", tags=["向量数据库"])
        self._register_routes()
        
        # 创建向量数据库目录
        os.makedirs(config.vector_db_path, exist_ok=True)
        
        # 初始化向量索引和元数据存储
        self.indexes = {}
        self.metadata = {}
        self.id_maps = {}
        
        # 加载现有索引
        self._load_indexes()
    
    def _load_indexes(self):
        """加载现有向量索引"""
        # 检查向量数据库目录中的索引文件
        for filename in os.listdir(self.config.vector_db_path):
            if filename.endswith(".index"):
                collection_name = filename[:-6]  # 移除.index后缀
                index_path = os.path.join(self.config.vector_db_path, filename)
                metadata_path = os.path.join(self.config.vector_db_path, f"{collection_name}.meta")
                
                # 加载索引
                try:
                    self.indexes[collection_name] = faiss.read_index(index_path)
                    
                    # 加载元数据
                    if os.path.exists(metadata_path):
                        with open(metadata_path, "r") as f:
                            self.metadata[collection_name] = json.load(f)
                            self.id_maps[collection_name] = {i: id for i, id in enumerate(self.metadata[collection_name].keys())}
                except Exception as e:
                    print(f"加载索引失败: {collection_name}, 错误: {str(e)}")
    
    def _save_index(self, collection: str):
        """保存向量索引"""
        if collection in self.indexes:
            index_path = os.path.join(self.config.vector_db_path, f"{collection}.index")
            metadata_path = os.path.join(self.config.vector_db_path, f"{collection}.meta")
            
            # 保存索引
            faiss.write_index(self.indexes[collection], index_path)
            
            # 保存元数据
            with open(metadata_path, "w") as f:
                json.dump(self.metadata[collection], f)
    
    def _get_or_create_index(self, collection: str) -> faiss.Index:
        """获取或创建向量索引"""
        if collection not in self.indexes:
            # 创建新索引
            self.indexes[collection] = faiss.IndexFlatL2(self.config.vector_dimension)
            self.metadata[collection] = {}
            self.id_maps[collection] = {}
        
        return self.indexes[collection]
    
    def _register_routes(self):
        """注册路由"""
        @self.router.post("/insert", response_model=VectorRecord)
        async def insert_vector(record: VectorRecord):
            """插入向量"""
            # 检查向量维度
            if len(record.vector) != self.config.vector_dimension:
                raise HTTPException(
                    status_code=400, 
                    detail=f"向量维度不匹配，期望: {self.config.vector_dimension}, 实际: {len(record.vector)}"
                )
            
            # 获取或创建索引
            index = self._get_or_create_index(record.collection)
            
            # 生成记录ID
            record_id = record.id or str(uuid.uuid4())
            
            # 准备元数据
            now = datetime.now().isoformat()
            metadata = record.metadata or {}
            metadata["created_at"] = now
            
            # 添加向量到索引
            vector_np = np.array([record.vector], dtype=np.float32)
            index.add(vector_np)
            
            # 更新元数据和ID映射
            idx = index.ntotal - 1
            if record.collection not in self.metadata:
                self.metadata[record.collection] = {}
            if record.collection not in self.id_maps:
                self.id_maps[record.collection] = {}
            
            self.metadata[record.collection][record_id] = metadata
            self.id_maps[record.collection][idx] = record_id
            
            # 保存索引
            self._save_index(record.collection)
            
            # 返回结果
            return VectorRecord(
                id=record_id,
                collection=record.collection,
                vector=record.vector,
                metadata=metadata,
                created_at=now
            )
        
        @self.router.post("/search", response_model=List[VectorSearchResult])
        async def search_vectors(query: VectorQuery):
            """搜索向量"""
            # 检查集合是否存在
            if query.collection not in self.indexes:
                raise HTTPException(status_code=404, detail=f"集合未找到: {query.collection}")
            
            # 检查向量维度
            if len(query.vector) != self.config.vector_dimension:
                raise HTTPException(
                    status_code=400, 
                    detail=f"向量维度不匹配，期望: {self.config.vector_dimension}, 实际: {len(query.vector)}"
                )
            
            # 获取索引
            index = self.indexes[query.collection]
            
            # 执行搜索
            vector_np = np.array([query.vector], dtype=np.float32)
            distances, indices = index.search(vector_np, query.top_k)
            
            # 准备结果
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx in self.id_maps[query.collection]:
                    record_id = self.id_maps[query.collection][idx]
                    metadata = self.metadata[query.collection].get(record_id, {})
                    results.append(VectorSearchResult(
                        id=record_id,
                        score=float(distances[0][i]),
                        metadata=metadata
                    ))
            
            return results
        
        @self.router.delete("/{collection}/{vector_id}")
        async def delete_vector(collection: str, vector_id: str):
            """删除向量"""
            # 检查集合是否存在
            if collection not in self.indexes:
                raise HTTPException(status_code=404, detail=f"集合未找到: {collection}")
            
            # 检查记录是否存在
            if vector_id not in self.metadata[collection]:
                raise HTTPException(status_code=404, detail=f"向量记录未找到: {vector_id}")
            
            # 删除记录
            # 注意：FAISS不支持直接删除，我们需要重建索引
            # 这是一个简化的实现，生产环境中应该使用更高效的方法
            
            # 获取所有向量和元数据
            all_vectors = []
            all_ids = []
            
            # 找到要删除的向量索引
            idx_to_delete = None
            for idx, id in self.id_maps[collection].items():
                if id == vector_id:
                    idx_to_delete = idx
                    break
            
            if idx_to_delete is None:
                raise HTTPException(status_code=404, detail=f"向量记录未找到: {vector_id}")
            
            # 删除元数据
            del self.metadata[collection][vector_id]
            
            # 重建索引
            new_index = faiss.IndexFlatL2(self.config.vector_dimension)
            new_id_map = {}
            
            # 复制所有向量（除了要删除的）
            for idx, id in self.id_maps[collection].items():
                if idx != idx_to_delete:
                    # 获取向量
                    vector = np.array([self.indexes[collection].reconstruct(idx)], dtype=np.float32)
                    new_index.add(vector)
                    new_id_map[new_index.ntotal - 1] = id
            
            # 更新索引和ID映射
            self.indexes[collection] = new_index
            self.id_maps[collection] = new_id_map
            
            # 保存索引
            self._save_index(collection)
            
            return {"message": f"向量记录已删除: {vector_id}"}
        
        @self.router.get("/collections")
        async def list_collections():
            """列出所有集合"""
            return {"collections": list(self.indexes.keys())}

def create_vector_module(config: MCPServerConfig) -> VectorModule:
    """创建向量数据库访问模块"""
    return VectorModule(config)
