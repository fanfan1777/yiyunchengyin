#!/usr/bin/env python3
"""
AI音乐生成器后端启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")

def check_dependencies():
    """检查并安装依赖"""
    requirements_file = Path("backend/requirements.txt")
    if not requirements_file.exists():
        print("❌ 错误: 找不到requirements.txt文件")
        sys.exit(1)
    
    print("📦 检查依赖包...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, capture_output=True, text=True)
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        sys.exit(1)

def check_env_file():
    """检查环境变量文件"""
    env_file = Path("backend/.env")
    env_example_candidates = [
        Path("backend/.env.example"),
        Path("backend/env.example"),
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

def start_server():
    """启动服务器"""
    print("🚀 启动AI音乐生成器后端服务...")
    print("=" * 50)
    
    # 切换到backend目录
    os.chdir("backend")
    
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
    
    # 目录创建已移除
    # create_directories()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
