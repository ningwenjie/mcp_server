# 通义千问(Qwen)调用MCP服务器示例说明

本文档详细介绍了如何使用通义千问(Qwen)调用MCP服务器的示例代码，包括客户端库的使用方法和具体示例。

## 目录

1. [客户端库介绍](#客户端库介绍)
2. [基本使用方法](#基本使用方法)
3. [详细示例](#详细示例)
4. [错误处理](#错误处理)
5. [最佳实践](#最佳实践)

## 客户端库介绍

`QwenMCPClient` 是一个专为通义千问(Qwen)设计的MCP服务器客户端库，它封装了与MCP服务器交互的所有必要功能，包括文件访问、向量操作、数据库操作和API调用等。

客户端库位于 `examples/qwen_client.py`，您可以将其复制到您的项目中使用。

## 基本使用方法

### 初始化客户端

```python
from qwen_client import QwenMCPClient

# 初始化客户端（不需要API密钥）
client = QwenMCPClient("http://localhost:8000")

# 初始化客户端（需要API密钥）
client = QwenMCPClient("http://localhost:8000", api_key="your_api_key")
```

### 文件操作

```python
# 上传文件
file_info = client.upload_file("path/to/your/file.txt")
print(f"文件ID: {file_info['id']}")
```

### 向量操作

```python
# 存储向量
vector = [0.1, 0.2, 0.3] * 512  # 假设向量维度为1536
metadata = {"text": "这是一个示例文本", "source": "通义千问"}
vector_info = client.store_vector("qwen_embeddings", vector, metadata)

# 搜索向量
query_vector = [0.15, 0.25, 0.35] * 512
search_results = client.search_vector("qwen_embeddings", query_vector, top_k=3)
```

### 数据库操作

```python
# 存储文档
document = {
    "title": "通义千问示例",
    "content": "这是通义千问生成的示例内容",
    "tags": ["AI", "NLP", "大模型"]
}
doc_info = client.store_document("qwen_documents", document)

# 查询文档
documents = client.find_documents("qwen_documents", {"tags": "AI"}, limit=5)
```

### API调用

```python
# 调用外部API
api_response = client.call_api(
    url="https://api.example.com/data",
    method="GET",
    params={"query": "通义千问"},
    headers={"Authorization": "Bearer token123"}
)
```

## 详细示例

以下是一个完整的示例，展示了如何使用通义千问(Qwen)与MCP服务器进行交互：

```python
import os
import numpy as np
from qwen_client import QwenMCPClient

def main():
    # 初始化客户端
    client = QwenMCPClient("http://localhost:8000")
    
    print("===== 通义千问(Qwen)调用MCP服务器示例 =====")
    
    # 示例1：文件上传和下载
    try:
        # 创建示例文件
        with open("example.txt", "w") as f:
            f.write("这是一个通义千问(Qwen)与MCP服务器集成的示例文件。")
        
        print("\n1. 文件上传示例:")
        file_info = client.upload_file("example.txt")
        print(f"文件上传成功: ID={file_info['id']}, 文件名={file_info['filename']}")
    except Exception as e:
        print(f"文件上传失败: {str(e)}")
    
    # 示例2：向量存储和搜索
    try:
        print("\n2. 向量存储和搜索示例:")
        
        # 模拟通义千问生成的向量（实际应用中应使用真实的模型生成向量）
        vector1 = np.random.rand(1536).tolist()  # 假设向量维度为1536
        vector2 = np.random.rand(1536).tolist()
        query_vector = np.random.rand(1536).tolist()
        
        # 存储向量
        metadata1 = {"text": "通义千问是阿里云推出的大型语言模型", "source": "示例1"}
        vector_info1 = client.store_vector("qwen_examples", vector1, metadata1)
        print(f"向量1存储成功: ID={vector_info1['id']}")
        
        metadata2 = {"text": "MCP服务器支持文件访问、数据库连接、API集成和向量数据库访问", "source": "示例2"}
        vector_info2 = client.store_vector("qwen_examples", vector2, metadata2)
        print(f"向量2存储成功: ID={vector_info2['id']}")
        
        # 搜索向量
        search_results = client.search_vector("qwen_examples", query_vector, top_k=2)
        print("向量搜索结果:")
        for i, result in enumerate(search_results):
            print(f"  结果{i+1}: ID={result['id']}, 相似度得分={result['score']}")
            print(f"  元数据: {result['metadata']}")
    except Exception as e:
        print(f"向量操作失败: {str(e)}")
    
    # 示例3：数据库操作
    try:
        print("\n3. 数据库操作示例:")
        
        # 存储文档
        document = {
            "title": "通义千问与MCP服务器集成示例",
            "content": "这是一个示例文档，展示如何使用通义千问调用MCP服务器的数据库功能。",
            "tags": ["通义千问", "MCP", "示例"],
            "model": "Qwen",
            "version": "1.0"
        }
        
        doc_info = client.store_document("qwen_documents", document)
        print(f"文档存储成功: ID={doc_info['id']}")
        
        # 查询文档
        query = {"model": "Qwen"}
        documents = client.find_documents("qwen_documents", query)
        print("文档查询结果:")
        for i, doc in enumerate(documents):
            print(f"  文档{i+1}: ID={doc['id']}")
            print(f"  数据: {doc['data']}")
    except Exception as e:
        print(f"数据库操作失败: {str(e)}")
    
    # 示例4：API调用
    try:
        print("\n4. API调用示例:")
        
        # 调用一个公共API
        api_response = client.call_api(
            url="https://httpbin.org/get",
            method="GET",
            params={"query": "通义千问", "model": "Qwen"}
        )
        
        print(f"API调用成功: 状态码={api_response['status_code']}")
        print(f"响应内容: {api_response['content']}")
    except Exception as e:
        print(f"API调用失败: {str(e)}")
    
    print("\n===== 示例执行完成 =====")

if __name__ == "__main__":
    main()
```

## 错误处理

客户端库中的所有方法都包含了错误处理，当发生错误时会抛出异常。建议使用try-except块来捕获和处理这些异常：

```python
try:
    result = client.some_method()
    # 处理结果
except Exception as e:
    print(f"操作失败: {str(e)}")
    # 处理错误
```

## 最佳实践

1. **向量维度匹配**：确保存储和查询的向量维度与MCP服务器配置的维度匹配（默认为1536）。

2. **批量操作**：对于大量数据，考虑使用批量操作而不是单个操作，以提高效率。

3. **错误重试**：对于网络请求，实现重试机制以处理临时性故障。

4. **资源清理**：在不再需要时，删除不必要的文件、向量和文档，以节省存储空间。

5. **安全性**：在生产环境中，始终启用API密钥验证，并使用HTTPS连接。

6. **监控和日志**：实现适当的日志记录和监控，以便及时发现和解决问题。

7. **与通义千问集成**：
   - 使用通义千问生成的嵌入向量进行语义搜索
   - 存储通义千问生成的内容到数据库
   - 使用MCP服务器作为通义千问的知识库和工具集成平台

## 进阶用例

### 使用通义千问进行语义搜索

```python
# 假设我们有一个函数可以从通义千问获取嵌入向量
def get_qwen_embedding(text):
    # 这里应该是调用通义千问API获取嵌入向量的代码
    # 为了示例，我们使用随机向量
    return np.random.rand(1536).tolist()

# 存储文档及其嵌入向量
documents = [
    "通义千问是阿里云推出的大型语言模型",
    "MCP服务器支持文件访问、数据库连接、API集成和向量数据库访问",
    "向量数据库可以用于语义搜索和相似度匹配"
]

for i, doc in enumerate(documents):
    # 获取文档的嵌入向量
    vector = get_qwen_embedding(doc)
    
    # 存储向量和元数据
    client.store_vector(
        "semantic_search",
        vector,
        {"text": doc, "doc_id": i}
    )

# 执行语义搜索
query = "如何使用向量数据库进行相似度搜索？"
query_vector = get_qwen_embedding(query)

results = client.search_vector("semantic_search", query_vector, top_k=1)
print(f"最相关的文档: {results[0]['metadata']['text']}")
```

### 构建知识库问答系统

```python
# 存储知识库文档
knowledge_base = [
    {"question": "什么是通义千问？", "answer": "通义千问是阿里云推出的大型语言模型。"},
    {"question": "MCP服务器有哪些功能？", "answer": "MCP服务器支持文件访问、数据库连接、API集成和向量数据库访问。"},
    {"question": "如何使用向量数据库？", "answer": "向量数据库可以用于语义搜索和相似度匹配。"}
]

# 存储知识库到向量数据库
for item in knowledge_base:
    # 获取问题的嵌入向量
    vector = get_qwen_embedding(item["question"])
    
    # 存储向量和元数据
    client.store_vector(
        "qa_system",
        vector,
        {"question": item["question"], "answer": item["answer"]}
    )

# 回答用户问题
user_question = "MCP服务器能做什么？"
question_vector = get_qwen_embedding(user_question)

results = client.search_vector("qa_system", question_vector, top_k=1)
print(f"问题: {user_question}")
print(f"回答: {results[0]['metadata']['answer']}")
```

这些示例展示了如何将通义千问与MCP服务器结合使用，构建强大的AI应用。
