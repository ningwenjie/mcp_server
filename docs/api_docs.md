# MCP服务器 API文档

## 概述

MCP服务器提供了一组RESTful API，用于文件访问、数据库连接、API集成和向量数据库访问。本文档详细介绍了这些API的使用方法。

## 基础URL

所有API的基础URL为：`http://<服务器地址>:<端口>`

默认情况下，如果在本地运行，基础URL为：`http://localhost:8000`

## 认证

如果启用了API密钥验证（通过设置`MCP_API_KEY_REQUIRED=true`），则需要在所有请求中包含`x-api-key`头部。

```
x-api-key: <您的API密钥>
```

## API端点

### 健康检查

#### 获取服务器状态

```
GET /health
```

**响应示例：**

```json
{
  "status": "healthy"
}
```

### 文件访问

#### 上传文件

```
POST /files/upload
```

**请求参数：**

- `file`：要上传的文件（表单数据）

**响应示例：**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "example.txt",
  "size": 1024,
  "content_type": "text/plain",
  "created_at": "2025-03-21T14:30:00.000Z",
  "path": "/app/storage/550e8400-e29b-41d4-a716-446655440000_example.txt"
}
```

#### 获取文件列表

```
GET /files/list
```

**响应示例：**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "example.txt",
    "size": 1024,
    "content_type": "text/plain",
    "created_at": "2025-03-21T14:30:00.000Z",
    "path": "/app/storage/550e8400-e29b-41d4-a716-446655440000_example.txt"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "filename": "example2.txt",
    "size": 2048,
    "content_type": "text/plain",
    "created_at": "2025-03-21T14:35:00.000Z",
    "path": "/app/storage/550e8400-e29b-41d4-a716-446655440001_example2.txt"
  }
]
```

#### 下载文件

```
GET /files/download/{file_id}
```

**路径参数：**

- `file_id`：文件ID

**响应：**

文件内容（二进制数据）

#### 删除文件

```
DELETE /files/{file_id}
```

**路径参数：**

- `file_id`：文件ID

**响应示例：**

```json
{
  "message": "文件已删除: 550e8400-e29b-41d4-a716-446655440000"
}
```

### 数据库连接

#### 插入记录

```
POST /database/insert
```

**请求体：**

```json
{
  "collection": "my_collection",
  "data": {
    "title": "示例文档",
    "content": "这是一个示例文档",
    "tags": ["示例", "文档"]
  }
}
```

**响应示例：**

```json
{
  "id": "6405e8400e29b41d4a7164466",
  "collection": "my_collection",
  "data": {
    "title": "示例文档",
    "content": "这是一个示例文档",
    "tags": ["示例", "文档"],
    "created_at": "2025-03-21T14:30:00.000Z",
    "updated_at": "2025-03-21T14:30:00.000Z"
  },
  "created_at": "2025-03-21T14:30:00.000Z",
  "updated_at": "2025-03-21T14:30:00.000Z"
}
```

#### 查询记录

```
GET /database/find/{collection}
```

**路径参数：**

- `collection`：集合名称

**查询参数：**

- `query`：JSON格式的查询条件（可选）
- `limit`：返回记录数量限制（默认为10）
- `skip`：跳过记录数量（默认为0）

**响应示例：**

```json
[
  {
    "id": "6405e8400e29b41d4a7164466",
    "collection": "my_collection",
    "data": {
      "title": "示例文档",
      "content": "这是一个示例文档",
      "tags": ["示例", "文档"],
      "created_at": "2025-03-21T14:30:00.000Z",
      "updated_at": "2025-03-21T14:30:00.000Z"
    },
    "created_at": "2025-03-21T14:30:00.000Z",
    "updated_at": "2025-03-21T14:30:00.000Z"
  }
]
```

#### 更新记录

```
PUT /database/update/{collection}/{record_id}
```

**路径参数：**

- `collection`：集合名称
- `record_id`：记录ID

**请求体：**

```json
{
  "title": "更新后的示例文档",
  "updated": true
}
```

**响应示例：**

```json
{
  "id": "6405e8400e29b41d4a7164466",
  "collection": "my_collection",
  "data": {
    "title": "更新后的示例文档",
    "content": "这是一个示例文档",
    "tags": ["示例", "文档"],
    "updated": true,
    "created_at": "2025-03-21T14:30:00.000Z",
    "updated_at": "2025-03-21T14:40:00.000Z"
  },
  "created_at": "2025-03-21T14:30:00.000Z",
  "updated_at": "2025-03-21T14:40:00.000Z"
}
```

#### 删除记录

```
DELETE /database/delete/{collection}/{record_id}
```

**路径参数：**

- `collection`：集合名称
- `record_id`：记录ID

**响应示例：**

```json
{
  "message": "记录已删除: 6405e8400e29b41d4a7164466"
}
```

#### 获取集合列表

```
GET /database/collections
```

**响应示例：**

```json
{
  "collections": ["my_collection", "another_collection"]
}
```

### API集成

#### 发送API请求

```
POST /api/request
```

**请求体：**

```json
{
  "url": "https://api.example.com/data",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer token123"
  },
  "params": {
    "query": "example"
  },
  "data": {
    "key": "value"
  },
  "timeout": 30,
  "service": "example_service"
}
```

**响应示例：**

```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/json",
    "content-length": "123"
  },
  "content": {
    "result": "success",
    "data": {
      "key": "value"
    }
  },
  "elapsed": 0.345
}
```

### 向量数据库访问

#### 插入向量

```
POST /vector/insert
```

**请求体：**

```json
{
  "collection": "my_vectors",
  "vector": [0.1, 0.2, 0.3, ...],
  "metadata": {
    "text": "这是一个示例文本",
    "source": "示例来源"
  }
}
```

**响应示例：**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "collection": "my_vectors",
  "vector": [0.1, 0.2, 0.3, ...],
  "metadata": {
    "text": "这是一个示例文本",
    "source": "示例来源",
    "created_at": "2025-03-21T14:30:00.000Z"
  },
  "created_at": "2025-03-21T14:30:00.000Z"
}
```

#### 搜索向量

```
POST /vector/search
```

**请求体：**

```json
{
  "collection": "my_vectors",
  "vector": [0.1, 0.2, 0.3, ...],
  "top_k": 5
}
```

**响应示例：**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "score": 0.95,
    "metadata": {
      "text": "这是一个示例文本",
      "source": "示例来源",
      "created_at": "2025-03-21T14:30:00.000Z"
    }
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "score": 0.85,
    "metadata": {
      "text": "这是另一个示例文本",
      "source": "示例来源",
      "created_at": "2025-03-21T14:35:00.000Z"
    }
  }
]
```

#### 删除向量

```
DELETE /vector/{collection}/{vector_id}
```

**路径参数：**

- `collection`：集合名称
- `vector_id`：向量ID

**响应示例：**

```json
{
  "message": "向量记录已删除: 550e8400-e29b-41d4-a716-446655440000"
}
```

#### 获取向量集合列表

```
GET /vector/collections
```

**响应示例：**

```json
{
  "collections": ["my_vectors", "another_vectors"]
}
```

## 错误处理

所有API在发生错误时都会返回适当的HTTP状态码和错误信息。

**错误响应示例：**

```json
{
  "detail": "文件未找到: 550e8400-e29b-41d4-a716-446655440000"
}
```

常见的HTTP状态码：

- `400 Bad Request`：请求参数错误
- `401 Unauthorized`：认证失败
- `404 Not Found`：资源未找到
- `500 Internal Server Error`：服务器内部错误

## 使用示例

### 使用curl上传文件

```bash
curl -X POST -F "file=@example.txt" http://localhost:8000/files/upload
```

### 使用Python发送API请求

```python
import requests

response = requests.post(
    "http://localhost:8000/api/request",
    json={
        "url": "https://api.example.com/data",
        "method": "GET",
        "params": {"query": "example"}
    }
)

print(response.json())
```

### 使用Python存储向量

```python
import requests
import numpy as np

# 生成随机向量
vector = np.random.rand(1536).tolist()

response = requests.post(
    "http://localhost:8000/vector/insert",
    json={
        "collection": "my_vectors",
        "vector": vector,
        "metadata": {"text": "示例文本"}
    }
)

print(response.json())
```
