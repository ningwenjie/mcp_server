"""
测试通义千问(Qwen)调用MCP服务器的集成示例
"""
import os
import sys
import time
import requests
from examples.qwen_client import QwenMCPClient

# 测试配置
MCP_SERVER_URL = "http://localhost:8000"
TEST_FILE_PATH = "qwen_test_file.txt"

def test_qwen_client():
    """测试通义千问客户端"""
    print("\n===== 测试通义千问(Qwen)调用MCP服务器 =====")
    
    # 等待服务器启动
    print("等待MCP服务器启动...")
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(f"{MCP_SERVER_URL}/health")
            if response.status_code == 200:
                print("MCP服务器已启动，开始测试...")
                break
        except:
            pass
        
        retry_count += 1
        print(f"尝试连接MCP服务器 ({retry_count}/{max_retries})...")
        time.sleep(2)
    
    if retry_count >= max_retries:
        print("❌ 无法连接到MCP服务器，请确保服务器已启动")
        return False
    
    # 初始化客户端
    client = QwenMCPClient(MCP_SERVER_URL)
    
    # 测试文件上传
    try:
        print("\n1. 测试文件上传...")
        
        # 创建测试文件
        with open(TEST_FILE_PATH, "w") as f:
            f.write("这是通义千问(Qwen)客户端测试文件。")
        
        file_info = client.upload_file(TEST_FILE_PATH)
        print(f"✅ 文件上传成功: ID={file_info['id']}, 文件名={file_info['filename']}")
    except Exception as e:
        print(f"❌ 文件上传失败: {str(e)}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(TEST_FILE_PATH):
            os.remove(TEST_FILE_PATH)
    
    # 测试向量存储和搜索
    try:
        print("\n2. 测试向量存储和搜索...")
        
        # 创建测试向量
        vector = [0.1] * 1536  # 假设向量维度为1536
        metadata = {"text": "通义千问测试向量", "source": "测试脚本"}
        
        # 存储向量
        vector_info = client.store_vector("qwen_test", vector, metadata)
        print(f"✅ 向量存储成功: ID={vector_info['id']}")
        
        # 搜索向量
        search_results = client.search_vector("qwen_test", vector, top_k=1)
        if len(search_results) > 0 and search_results[0]["id"] == vector_info["id"]:
            print(f"✅ 向量搜索成功，找到匹配向量")
        else:
            print(f"❌ 向量搜索失败，未找到匹配向量")
            return False
    except Exception as e:
        print(f"❌ 向量操作失败: {str(e)}")
        return False
    
    # 测试数据库操作
    try:
        print("\n3. 测试数据库操作...")
        
        # 存储文档
        document = {
            "title": "通义千问测试文档",
            "content": "这是一个测试文档",
            "tags": ["测试", "通义千问"]
        }
        
        doc_info = client.store_document("qwen_test_docs", document)
        print(f"✅ 文档存储成功: ID={doc_info['id']}")
        
        # 查询文档
        documents = client.find_documents("qwen_test_docs", {"tags": "通义千问"})
        if len(documents) > 0:
            print(f"✅ 文档查询成功，找到{len(documents)}个匹配文档")
        else:
            print(f"❌ 文档查询失败，未找到匹配文档")
            return False
    except Exception as e:
        print(f"❌ 数据库操作失败: {str(e)}")
        return False
    
    # 测试API调用
    try:
        print("\n4. 测试API调用...")
        
        api_response = client.call_api(
            url="https://httpbin.org/get",
            method="GET",
            params={"source": "qwen_test"}
        )
        
        if api_response["status_code"] == 200:
            print(f"✅ API调用成功")
        else:
            print(f"❌ API调用失败: {api_response}")
            return False
    except Exception as e:
        print(f"❌ API调用失败: {str(e)}")
        return False
    
    print("\n✅ 通义千问(Qwen)客户端测试全部通过！")
    return True

if __name__ == "__main__":
    success = test_qwen_client()
    sys.exit(0 if success else 1)
