# MCP服务器项目说明

## 项目概述

MCP（多功能计算平台）服务器是一个功能强大的后端服务，支持文件访问、数据库连接、API集成和向量数据库访问等多种功能。本项目专为与通义千问(Qwen)等大型语言模型集成而设计，提供了完整的Docker部署配置和通义千问调用示例。

## 项目结构

```
mcp_server/
├── src/                    # 源代码目录
│   ├── __init__.py         # 初始化模块
│   ├── config.py           # 配置管理
│   ├── server.py           # 服务器主类
│   └── modules/            # 功能模块
│       ├── __init__.py     # 模块注册
│       ├── file_module.py  # 文件访问模块
│       ├── database_module.py # 数据库连接模块
│       ├── api_module.py   # API集成模块
│       └── vector_module.py # 向量数据库模块
├── docker/                 # Docker配置
│   ├── Dockerfile          # Docker镜像配置
│   └── docker-compose.yml  # Docker Compose配置
├── examples/               # 示例代码
│   ├── qwen_client.py      # 通义千问客户端库
│   └── qwen_example.py     # 通义千问使用示例
├── docs/                   # 文档
│   ├── user_guide.md       # 用户指南
│   ├── api_docs.md         # API文档
│   └── qwen_examples.md    # 通义千问示例说明
├── test_server.py          # 服务器测试脚本
├── test_qwen_client.py     # 通义千问客户端测试脚本
├── main.py                 # 主入口文件
└── requirements.txt        # 依赖列表
```

## 功能特性

- **文件访问**：上传、下载、列表和删除文件
- **数据库连接**：MongoDB集成，支持文档的增删改查
- **API集成**：支持调用外部API服务
- **向量数据库**：支持向量存储和相似度搜索
- **Docker部署**：完整的Docker配置，支持一键部署
- **通义千问集成**：提供通义千问调用MCP服务器的客户端和示例

## 快速开始

### 安装

1. 克隆项目代码：

```bash
git clone https://github.com/ningwenjie/mcp_server
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

### 使用通义千问客户端

```python
from examples.qwen_client import QwenMCPClient

# 初始化客户端
client = QwenMCPClient("http://localhost:8000")

# 上传文件
file_info = client.upload_file("example.txt")

# 存储向量
vector = [0.1, 0.2, 0.3] * 512  # 1536维向量
metadata = {"text": "这是一个示例文本", "source": "通义千问"}
vector_info = client.store_vector("qwen_embeddings", vector, metadata)

# 搜索向量
query_vector = [0.15, 0.25, 0.35] * 512
search_results = client.search_vector("qwen_embeddings", query_vector, top_k=3)
```

## 文档

详细文档请参阅：

- [用户指南](docs/user_guide.md)：安装、配置和基本使用
- [API文档](docs/api_docs.md)：详细的API参考
- [通义千问示例说明](docs/qwen_examples.md)：通义千问集成示例

## 测试

运行服务器测试：

```bash
python test_server.py
```

运行通义千问客户端测试：

```bash
python test_qwen_client.py
```

## 依赖

- Python 3.10+
- FastAPI
- Uvicorn
- PyMongo
- FAISS
- Docker (用于部署)

详细依赖列表请参阅 `requirements.txt`。

## 许可证

[MIT License](LICENSE)
