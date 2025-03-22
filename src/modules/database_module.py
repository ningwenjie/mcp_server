"""
MCP服务器数据库连接模块
"""
import os
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import pymongo
from datetime import datetime
import json
from bson import ObjectId

from ..config import MCPServerConfig
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def mongo_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
class DatabaseRecord(BaseModel):
    """数据库记录模型"""
    id: Optional[str] = None
    collection: str
    data: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class DatabaseModule:
    """数据库连接模块"""
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.router = APIRouter(prefix="/database", tags=["数据库连接"])
        self._register_routes()

        # 连接MongoDB
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client[config.mongodb_db_name]

    def _register_routes(self):
        """注册路由"""
        @self.router.post("/insert", response_model=DatabaseRecord)
        async def insert_record(record: DatabaseRecord):
            """插入记录"""
            # 准备数据
            data = record.data
            now = datetime.now().isoformat()
            data["created_at"] = now
            data["updated_at"] = now

            # 插入数据
            collection = self.db[record.collection]
            result = collection.insert_one(data)

            # 返回结果
            return DatabaseRecord(
                id=str(result.inserted_id),
                collection=record.collection,
                data=data,
                created_at=now,
                updated_at=now
            )

        @self.router.get("/find/{collection}", response_model=List[DatabaseRecord])
        async def find_records(
            collection: str,
            query: Optional[str] = Query(None, description="JSON格式的查询条件"),
            limit: int = Query(10, description="返回记录数量限制"),
            skip: int = Query(0, description="跳过记录数量")
        ):
            """查询记录"""
            # 解析查询条件
            query_dict = {}
            if query:
                try:
                    query_dict = json.loads(query)
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="无效的查询条件格式")

            # 执行查询
            db_collection = self.db[collection]
            cursor = db_collection.find(query_dict).skip(skip).limit(limit)

            # 返回结果
            results = []
            for doc in cursor:
                # 转换ObjectId为字符串
                doc_id = str(doc.pop("_id", None))
                results.append(DatabaseRecord(
                    id=doc_id,
                    collection=collection,
                    data=doc,
                    created_at=doc.get("created_at"),
                    updated_at=doc.get("updated_at")
                ))

            return results

        @self.router.put("/update/{collection}/{record_id}", response_model=DatabaseRecord)
        async def update_record(
            collection: str,
            record_id: str,
            data: Dict[str, Any] = Body(...)
        ):
            """更新记录"""
            # 准备数据
            now = datetime.now().isoformat()
            data["updated_at"] = now

            # 转换记录ID
            try:
                from bson.objectid import ObjectId
                obj_id = ObjectId(record_id)
            except Exception:
                raise HTTPException(status_code=400, detail="无效的记录ID格式")

            # 更新数据
            db_collection = self.db[collection]
            result = db_collection.update_one({"_id": obj_id}, {"$set": data})

            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail=f"记录未找到: {record_id}")

            # 获取更新后的记录
            updated_doc = db_collection.find_one({"_id": obj_id})
            if not updated_doc:
                raise HTTPException(status_code=404, detail=f"记录未找到: {record_id}")

            # 转换ObjectId为字符串
            doc_id = str(updated_doc.pop("_id", None))

            return DatabaseRecord(
                id=doc_id,
                collection=collection,
                data=updated_doc,
                created_at=updated_doc.get("created_at"),
                updated_at=updated_doc.get("updated_at")
            )

        @self.router.delete("/delete/{collection}/{record_id}")
        async def delete_record(collection: str, record_id: str):
            """删除记录"""
            # 转换记录ID
            try:
                from bson.objectid import ObjectId
                obj_id = ObjectId(record_id)
            except Exception:
                raise HTTPException(status_code=400, detail="无效的记录ID格式")

            # 删除数据
            db_collection = self.db[collection]
            result = db_collection.delete_one({"_id": obj_id})

            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail=f"记录未找到: {record_id}")

            return {"message": f"记录已删除: {record_id}"}

        @self.router.get("/collections")
        async def list_collections():
            """列出所有集合"""
            collections = self.db.list_collection_names()
            return {"collections": collections}

def create_database_module(config: MCPServerConfig) -> DatabaseModule:
    """创建数据库连接模块"""
    return DatabaseModule(config)
