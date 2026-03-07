"""命令行接口"""

import argparse
import sys

from recipe_agent import __version__


def main():
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        description="Recipe Agent - 个性化多模态菜谱 Agent"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"Recipe Agent v{__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # serve 命令
    serve_parser = subparsers.add_parser("serve", help="启动 API 服务")
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="监听地址（默认：0.0.0.0）"
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="监听端口（默认：8000）"
    )
    serve_parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载（开发模式）"
    )
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成菜谱")
    gen_parser.add_argument(
        "text",
        help="自然语言输入（如：番茄炒蛋）"
    )
    gen_parser.add_argument(
        "--output",
        "-o",
        help="输出文件路径（JSON 格式）"
    )
    
    args = parser.parse_args()
    
    if args.command == "serve":
        import uvicorn
        uvicorn.run(
            "recipe_agent.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    
    elif args.command == "generate":
        print(f"🍳 生成菜谱：{args.text}")
        print("⚠️ 功能开发中，敬请期待")
        # TODO: 实现命令行生成逻辑
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
