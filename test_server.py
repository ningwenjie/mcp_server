"""
MCP服务器测试脚本
"""
import os
import sys
import json
import requests
import numpy as np
import time

# 测试配置
MCP_SERVER_URL = "http://localhost:8000"
TEST_FILE_PATH = "test_file.txt"
TEST_VECTOR_DIMENSION = 1536

def test_health_check():
    """测试健康检查接口"""
    print("\n测试健康检查接口...")
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health")
        if response.status_code == 200 and response.json()["status"] == "healthy":
            print("✅ 健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def test_file_module():
    """测试文件访问模块"""
    print("\n测试文件访问模块...")
    
    # 创建测试文件
    with open(TEST_FILE_PATH, "w") as f:
        f.write("这是一个测试文件，用于测试MCP服务器的文件访问模块。")
    
    try:
        # 测试文件上传
        print("测试文件上传...")
        files = {"file": open(TEST_FILE_PATH, "rb")}
        response = requests.post(f"{MCP_SERVER_URL}/files/upload", files=files)
        files["file"].close()
        
        if response.status_code != 200:
            print(f"❌ 文件上传失败: {response.text}")
            return False
        
        file_info = response.json()
        file_id = file_info["id"]
        print(f"✅ 文件上传成功: ID={file_id}")
        
        # 测试文件列表
        print("测试文件列表...")
        response = requests.get(f"{MCP_SERVER_URL}/files/list")
        if response.status_code != 200:
            print(f"❌ 获取文件列表失败: {response.text}")
            return False
        
        files_list = response.json()
        if not any(f["id"] == file_id for f in files_list):
            print(f"❌ 上传的文件未在列表中找到")
            return False
        
        print(f"✅ 文件列表获取成功，找到上传的文件")
        
        # 测试文件下载
        print("测试文件下载...")
        response = requests.get(f"{MCP_SERVER_URL}/files/download/{file_id}")
        if response.status_code != 200:
            print(f"❌ 文件下载失败: {response.text}")
            return False
        
        print(f"✅ 文件下载成功")
        
        # 测试文件删除
        print("测试文件删除...")
        response = requests.delete(f"{MCP_SERVER_URL}/files/{file_id}")
        if response.status_code != 200:
            print(f"❌ 文件删除失败: {response.text}")
            return False
        
        print(f"✅ 文件删除成功")
        
        # 验证文件已删除
        response = requests.get(f"{MCP_SERVER_URL}/files/list")
        files_list = response.json()
        if any(f["id"] == file_id for f in files_list):
            print(f"❌ 文件删除后仍在列表中")
            return False
        
        print(f"✅ 文件访问模块测试通过")
        return True
    
    except Exception as e:
        print(f"❌ 文件访问模块测试异常: {str(e)}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(TEST_FILE_PATH):
            os.remove(TEST_FILE_PATH)

def test_database_module():
    """测试数据库连接模块"""
    print("\n测试数据库连接模块...")
    
    try:
        # 测试插入记录
        print("测试插入记录...")
        test_data = {
            "collection": "test_collection",
            "data": {
                "title": "测试文档",
                "content": "这是一个测试文档，用于测试MCP服务器的数据库连接模块。",
                "tags": ["测试", "MCP", "数据库"]
            }
        }
        
        response = requests.post(
            f"{MCP_SERVER_URL}/database/insert",
            json=test_data
        )
        
        if response.status_code != 200:
            print(f"❌ 插入记录失败: {response.text}")
            return False
        
        record_info = response.json()
        record_id = record_info["id"]
        print(f"✅ 插入记录成功: ID={record_id}")
        
        # 测试查询记录
        print("测试查询记录...")
        response = requests.get(
            f"{MCP_SERVER_URL}/database/find/test_collection"
        )
        
        if response.status_code != 200:
            print(f"❌ 查询记录失败: {response.text}")
            return False
        
        records = response.json()
        if not any(r["id"] == record_id for r in records):
            print(f"❌ 插入的记录未在查询结果中找到")
            return False
        
        print(f"✅ 查询记录成功，找到插入的记录")
        
        # 测试更新记录
        print("测试更新记录...")
        update_data = {
            "title": "更新后的测试文档",
            "updated": True
        }
        
        response = requests.put(
            f"{MCP_SERVER_URL}/database/update/test_collection/{record_id}",
            json=update_data
        )
        
        if response.status_code != 200:
            print(f"❌ 更新记录失败: {response.text}")
            return False
        
        updated_record = response.json()
        if not updated_record["data"].get("updated"):
            print(f"❌ 记录未正确更新")
            return False
        
        print(f"✅ 更新记录成功")
        
        # 测试删除记录
        print("测试删除记录...")
        response = requests.delete(
            f"{MCP_SERVER_URL}/database/delete/test_collection/{record_id}"
        )
        
        if response.status_code != 200:
            print(f"❌ 删除记录失败: {response.text}")
            return False
        
        print(f"✅ 删除记录成功")
        
        # 验证记录已删除
        response = requests.get(
            f"{MCP_SERVER_URL}/database/find/test_collection"
        )
        
        records = response.json()
        if any(r["id"] == record_id for r in records):
            print(f"❌ 记录删除后仍在查询结果中")
            return False
        
        print(f"✅ 数据库连接模块测试通过")
        return True
    
    except Exception as e:
        print(f"❌ 数据库连接模块测试异常: {str(e)}")
        return False

def test_api_module():
    """测试API集成模块"""
    print("\n测试API集成模块...")
    
    try:
        # 测试API请求
        print("测试API请求...")
        test_request = {
            "url": "https://httpbin.org/get",
            "method": "GET",
            "params": {
                "test": "value",
                "source": "mcp_server_test"
            }
        }
        
        response = requests.post(
            f"{MCP_SERVER_URL}/api/request",
            json=test_request
        )
        
        if response.status_code != 200:
            print(f"❌ API请求失败: {response.text}")
            return False
        
        api_response = response.json()
        if api_response["status_code"] != 200:
            print(f"❌ API响应状态码错误: {api_response['status_code']}")
            return False
        
        # 验证API响应内容
        content = api_response["content"]
        if not isinstance(content, dict) or not content.get("args") or content["args"].get("source") != "mcp_server_test":
            print(f"❌ API响应内容错误: {content}")
            return False
        
        print(f"✅ API请求成功，响应内容正确")
        print(f"✅ API集成模块测试通过")
        return True
    
    except Exception as e:
        print(f"❌ API集成模块测试异常: {str(e)}")
        return False

def test_vector_module():
    """测试向量数据库访问模块"""
    print("\n测试向量数据库访问模块...")
    
    try:
        # 生成测试向量
        vector1 = np.random.rand(TEST_VECTOR_DIMENSION).tolist()
        vector2 = np.random.rand(TEST_VECTOR_DIMENSION).tolist()
        query_vector = np.random.rand(TEST_VECTOR_DIMENSION).tolist()
        
        # 测试插入向量
        print("测试插入向量...")
        test_vector1 = {
            "collection": "test_vectors",
            "vector": vector1,
            "metadata": {
                "description": "测试向量1",
                "source": "测试脚本"
            }
        }
        
        response = requests.post(
            f"{MCP_SERVER_URL}/vector/insert",
            json=test_vector1
        )
        
        if response.status_code != 200:
            print(f"❌ 插入向量1失败: {response.text}")
            return False
        
        vector_info1 = response.json()
        vector_id1 = vector_info1["id"]
        print(f"✅ 插入向量1成功: ID={vector_id1}")
        
        # 插入第二个向量
        test_vector2 = {
            "collection": "test_vectors",
            "vector": vector2,
            "metadata": {
                "description": "测试向量2",
                "source": "测试脚本"
            }
        }
        
        response = requests.post(
            f"{MCP_SERVER_URL}/vector/insert",
            json=test_vector2
        )
        
        if response.status_code != 200:
            print(f"❌ 插入向量2失败: {response.text}")
            return False
        
        vector_info2 = response.json()
        vector_id2 = vector_info2["id"]
        print(f"✅ 插入向量2成功: ID={vector_id2}")
        
        # 测试向量搜索
        print("测试向量搜索...")
        test_query = {
            "collection": "test_vectors",
            "vector": query_vector,
            "top_k": 2
        }
        
        response = requests.post(
            f"{MCP_SERVER_URL}/vector/search",
            json=test_query
        )
        
        if response.status_code != 200:
            print(f"❌ 向量搜索失败: {response.text}")
            return False
        
        search_results = response.json()
        if len(search_results) != 2:
            print(f"❌ 向量搜索结果数量错误: {len(search_results)}")
            return False
        
        print(f"✅ 向量搜索成功，返回了{len(search_results)}个结果")
        
        # 测试删除向量
        print("测试删除向量...")
        response = requests.delete(
            f"{MCP_SERVER_URL}/vector/test_vectors/{vector_id1}"
        )
        
        if response.status_code != 200:
            print(f"❌ 删除向量失败: {response.text}")
            return False
        
        print(f"✅ 删除向量成功")
        
        # 验证向量已删除
        test_query["top_k"] = 1
        response = requests.post(
            f"{MCP_SERVER_URL}/vector/search",
            json=test_query
        )
        
        search_results = response.json()
        if len(search_results) != 1 or search_results[0]["id"] == vector_id1:
            print(f"❌ 向量删除后仍在搜索结果中")
            return False
        
        print(f"✅ 向量数据库访问模块测试通过")
        return True
    
    except Exception as e:
        print(f"❌ 向量数据库访问模块测试异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("===== MCP服务器功能测试 =====")
    
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
    
    # 运行测试
    tests = [
        ("健康检查", test_health_check),
        ("文件访问模块", test_file_module),
        ("数据库连接模块", test_database_module),
        ("API集成模块", test_api_module),
        ("向量数据库访问模块", test_vector_module)
    ]
    
    results = {}
    all_passed = True
    
    for name, test_func in tests:
        print(f"\n===== 测试 {name} =====")
        result = test_func()
        results[name] = result
        if not result:
            all_passed = False
    
    # 打印测试结果摘要
    print("\n===== 测试结果摘要 =====")
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    if all_passed:
        print("\n✅ 所有测试通过！MCP服务器功能正常。")
    else:
        print("\n❌ 部分测试失败，请检查详细输出。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
