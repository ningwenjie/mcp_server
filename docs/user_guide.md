# MCP服务器使用指南

## 简介

MCP（多功能计算平台）服务器是一个功能强大的后端服务，支持文件访问、数据库连接、API集成和向量数据库访问等多种功能。本服务器设计用于与大型语言模型（如通义千问Qwen）集成，为AI应用提供强大的后端支持。

## 目录

1. [安装指南](#安装指南)
2. [功能概述](#功能概述)
3. [API文档](#api文档)
4. [通义千问(Qwen)集成](#通义千问集成)
5. [示例说明](#示例说明)
6. [常见问题](#常见问题)

## 安装指南

### 前提条件

- Docker 和 Docker Compose
- 互联网连接（用于拉取Docker镜像）

### 安装步骤

1. 克隆项目代码：

```bash
git clone <项目仓库URL>
cd mcp_server
```

2. 使用Docker Compose启动服务：

```bash
docker-compose -f docker/docker-compose.yml up -d
```

3. 验证服务是否正常运行：

```bash
curl http://localhost:8000/health
```

如果返回 `{"status":"healthy"}`，则表示服务已成功启动。

### 配置选项

MCP服务器支持通过环境变量进行配置。主要配置选项包括：

| 环境变量 | 描述 | 默认值 |
|---------|------|-------|
| MCP_HOST | 服务器监听地址 | 0.0.0.0 |
| MCP_PORT | 服务器监听端口 | 8000 |
| MCP_DEBUG | 是否启用调试模式 | false |
| MCP_FILE_STORAGE_PATH | 文件存储路径 | /app/storage |
| MCP_VECTOR_DB_PATH | 向量数据库路径 | /app/vector_db |
| MCP_MONGODB_URI | MongoDB连接URI | mongodb://mongodb:27017 |
| MCP_MONGODB_DB_NAME | MongoDB数据库名称 | mcp_server_db |
| MCP_API_KEY_REQUIRED | 是否启用API密钥验证 | false |

可以在`docker-compose.yml`文件中的`environment`部分修改这些配置。

## 功能概述

MCP服务器提供以下核心功能：

### 1. 文件访问

- 文件上传：支持上传各种类型的文件
- 文件下载：通过文件ID下载文件
- 文件列表：获取所有已上传文件的列表
- 文件删除：删除指定的文件

### 2. 数据库连接

- 文档存储：将数据存储到MongoDB数据库
- 文档查询：根据条件查询文档
- 文档更新：更新现有文档
- 文档删除：删除指定文档

### 3. API集成

- API请求代理：通过MCP服务器发送HTTP请求到外部API
- 支持各种HTTP方法（GET、POST、PUT、DELETE等）
- 支持请求参数、请求体和自定义头部

### 4. 向量数据库访问

- 向量存储：存储高维向量数据和相关元数据
- 向量搜索：基于相似度搜索向量
- 向量删除：删除指定的向量记录

## API文档

启动服务后，可以通过访问 `http://localhost:8000/docs` 查看完整的API文档（Swagger UI）。

### 主要API端点

#### 文件访问

- `POST /files/upload`：上传文件
- `GET /files/list`：获取文件列表
- `GET /files/download/{file_id}`：下载文件
- `DELETE /files/{file_id}`：删除文件

#### 数据库连接

- `POST /database/insert`：插入文档
- `GET /database/find/{collection}`：查询文档
- `PUT /database/update/{collection}/{record_id}`：更新文档
- `DELETE /database/delete/{collection}/{record_id}`：删除文档
- `GET /database/collections`：获取集合列表

#### API集成

- `POST /api/request`：发送API请求

#### 向量数据库访问

- `POST /vector/insert`：插入向量
- `POST /vector/search`：搜索向量
- `DELETE /vector/{collection}/{vector_id}`：删除向量
- `GET /vector/collections`：获取向量集合列表

## 通义千问集成

MCP服务器专为与通义千问(Qwen)等大型语言模型集成而设计。我们提供了一个Python客户端库，简化了通义千问与MCP服务器的交互。

### 客户端安装

```bash
# 将客户端文件复制到您的项目中
cp examples/qwen_client.py /path/to/your/project/
```

### 基本用法

```python
from qwen_client import QwenMCPClient

# 初始化客户端
client = QwenMCPClient("http://localhost:8000")

# 上传文件
file_info = client.upload_file("example.txt")

# 存储向量
vector = [0.1, 0.2, 0.3] * 512  # 1536维向量
metadata = {"text": "这是一个示例文本", "source": "通义千问"}
vector_info = client.store_vector("qwen_embeddings", vector, metadata)

# 搜索向量
query_vector = [0.15, 0.25, 0.35] * 512  # 1536维向量
search_results = client.search_vector("qwen_embeddings", query_vector, top_k=3)

# 存储文档
document = {
    "title": "通义千问示例",
    "content": "这是通义千问生成的示例内容",
    "tags": ["AI", "NLP", "大模型"]
}
doc_info = client.store_document("qwen_documents", document)

# 调用外部API
api_response = client.call_api(
    url="https://api.example.com/data",
    method="GET",
    params={"query": "通义千问"}
)
```

## 示例说明

项目包含以下示例代码：

### 1. 基本使用示例

`examples/qwen_example.py` 展示了如何使用QwenMCPClient与MCP服务器交互，包括文件上传、向量操作、数据库操作和API调用等示例。

运行示例：

```bash
python examples/qwen_example.py
```

### 2. 测试脚本

`test_server.py` 是一个全面的测试脚本，用于测试MCP服务器的所有功能模块。

运行测试：

```bash
python test_server.py
```

`test_qwen_client.py` 用于测试通义千问客户端与MCP服务器的集成。

运行测试：

```bash
python test_qwen_client.py
```

## 常见问题

### Q: 如何更改服务器端口？

A: 在`docker-compose.yml`文件中修改`ports`部分和`MCP_PORT`环境变量。

### Q: 如何启用API密钥验证？

A: 在`docker-compose.yml`文件中将`MCP_API_KEY_REQUIRED`设置为`true`，并添加`MCP_API_KEYS`环境变量，格式为`"service1:key1,service2:key2"`。

### Q: 数据存储在哪里？

A: 文件存储在Docker卷`mcp_storage`中，向量数据库存储在`mcp_vector_db`中，MongoDB数据存储在`mongodb_data`中。这些卷确保数据在容器重启后仍然保留。

### Q: 如何备份数据？

A: 可以使用Docker卷备份命令备份数据卷，或者使用MongoDB的备份工具备份数据库。

### Q: 如何扩展MCP服务器的功能？

A: 可以通过添加新的模块到`src/modules/`目录，并在`src/modules/__init__.py`中注册新模块来扩展功能。
