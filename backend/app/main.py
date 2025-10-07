import os
from dotenv import load_dotenv

# 加载环境变量（提前，优先于任何依赖环境的模块导入）
load_dotenv()

from app.models.db import SessionLocal
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from sqlalchemy import text  

# 创建FastAPI应用
app = FastAPI(
    title="意韵成音",
    description="基于多模态AI的智能音乐生成平台",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "AI音乐生成器API服务正在运行", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务运行正常"}

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    # 测试数据库连接
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # 确保只用 text() 包裹
        db.close()
        print("MySQL 数据库连接成功！")
    except Exception as e:
        import traceback
        print(f"数据库连接失败: {e}")
        traceback.print_exc()

    # 自动创建所有模型表
    from app.models.db import create_tables
    create_tables()

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
