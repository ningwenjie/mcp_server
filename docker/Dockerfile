FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY src/ ./src/
COPY main.py .

# 创建存储目录
RUN mkdir -p /app/storage /app/vector_db

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV MCP_DEBUG=false
ENV MCP_FILE_STORAGE_PATH=/app/storage
ENV MCP_VECTOR_DB_PATH=/app/vector_db
ENV MCP_MONGODB_URI=mongodb://mongodb:27017
ENV MCP_MONGODB_DB_NAME=mcp_server_db
ENV MCP_API_KEY_REQUIRED=false

# 启动命令
CMD ["python", "main.py"]
