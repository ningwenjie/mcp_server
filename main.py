"""
MCP服务器主入口文件
"""
import os
import argparse
from src import create_server, MCPServerConfig

def main():
    """MCP服务器主入口函数"""
    parser = argparse.ArgumentParser(description="MCP服务器")
    parser.add_argument("--host", type=str, help="服务器主机地址")
    parser.add_argument("--port", type=int, help="服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 从环境变量或命令行参数创建配置
    config = MCPServerConfig.from_env()
    
    # 命令行参数优先级高于环境变量
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port
    if args.debug:
        config.debug = args.debug
    
    # 创建并运行服务器
    server = create_server(config)
    server.run()

if __name__ == "__main__":
    main()
