#!/usr/bin/env python3
"""
AI音乐生成器后端启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")

def check_dependencies():
    """检查并安装依赖"""
    requirements_file = BACKEND_DIR / "requirements.txt"
    if not requirements_file.exists():
        print(f"❌ 错误: 找不到requirements.txt文件: {requirements_file}")
        sys.exit(1)
    
    print("📦 检查依赖包...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, text=True)
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        sys.exit(1)

def check_env_file():
    """检查环境变量文件"""
    env_file = BACKEND_DIR / ".env"
    env_example_candidates = [
        BACKEND_DIR / ".env.example",
        BACKEND_DIR / "env.example",
    ]
    
    if not env_file.exists():
        for candidate in env_example_candidates:
            if candidate.exists():
                print(f"📝 复制 {candidate.name} 到 .env")
                env_file.write_text(candidate.read_text())
                print("✅ .env文件创建完成")
                break
        else:
            print("❌ 错误: 找不到 .env 或 env.example/.env.example，请手动创建 backend/.env")
            sys.exit(1)
    else:
        print("✅ .env文件检查通过")

def create_directories():
    """创建必要的目录（已禁用，不再创建本地uploads/generated_music）"""
    # 不再创建任何本地目录，以使用在线资源
    pass

def load_backend_env():
    """显式加载 backend/.env 到当前进程环境"""
    env_path = BACKEND_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ 已加载 backend/.env 环境变量")
    else:
        print("⚠️ 未找到 backend/.env，将依赖系统环境变量")

def check_database_and_migrate():
    """检查数据库连接并创建表"""
    try:
        # 确保 backend 在模块搜索路径中
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))
        from sqlalchemy import text as sa_text
        from app.models.db import SessionLocal, create_tables
        # 测试连接
        db = SessionLocal()
        db.execute(sa_text("SELECT 1"))
        db.close()
        print("✅ MySQL 数据库连接成功！")
    except Exception as e:
        print(f"⚠️ 数据库连接检查失败: {e}")
    try:
        from app.models.db import create_tables
        create_tables()
        print("✅ 数据库表创建/校验完成")
    except Exception as e:
        print(f"⚠️ 创建数据库表失败: {e}")

def start_server():
    """启动服务器"""
    print("🚀 启动AI音乐生成器后端服务...")
    print("=" * 50)
    
    # 切换到backend目录
    os.chdir(str(BACKEND_DIR))
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")

def main():
    """主函数"""
    print("🎵 AI音乐生成器 - 后端启动脚本")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 检查并安装依赖
    check_dependencies()
    
    # 检查环境变量文件
    check_env_file()
    # 加载环境变量
    load_backend_env()
    # 检查数据库并创建表
    check_database_and_migrate()
    
    # 目录创建已移除
    # create_directories()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
