"""
通义千问(Qwen)调用MCP服务器的使用示例
"""
import os
import numpy as np
from qwen_client import QwenMCPClient

def main():
    """主函数"""
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
