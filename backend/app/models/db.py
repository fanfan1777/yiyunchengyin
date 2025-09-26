import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 加载环境变量（确保无论导入顺序如何，都能读取到 .env）
load_dotenv()

# 优先支持 DATABASE_URL，其次从单项 MYSQL_* 变量拼接
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB = os.getenv("MYSQL_DB")

    if not (MYSQL_USER and MYSQL_PASSWORD and MYSQL_DB):
        raise RuntimeError(
            "数据库环境变量未正确配置，请设置 DATABASE_URL 或 MYSQL_USER、MYSQL_PASSWORD、MYSQL_DB 等变量。"
        )

    DATABASE_URL = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

SQL_ECHO = os.getenv("SQL_ECHO", "False").lower() == "true"

engine = create_engine(DATABASE_URL, echo=SQL_ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 创建所有表的函数
from app.models.models import User

def create_tables():
    Base.metadata.create_all(bind=engine)

# 在需要的地方导入 SessionLocal 获取数据库会话
