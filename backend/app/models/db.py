import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text as sa_text
import pathlib

# 加载环境变量（确保无论导入顺序如何，都能读取到 .env）
load_dotenv()

# 优先支持 DATABASE_URL，其次从单项 MYSQL_* 变量拼接；若连接失败，可回退到SQLite
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
# 默认不允许回退到本地 SQLite（改为严格依赖 MySQL）
FALLBACK_TO_SQLITE = os.getenv("DB_FALLBACK_TO_SQLITE", "false").lower() == "true"

# SQLite 备用数据库路径（默认使用仓库内 backend/app.db）
BASE_DIR = pathlib.Path(__file__).resolve().parents[2]  # 指向 backend 目录
SQLITE_PATH = BASE_DIR / "app.db"
SQLITE_URL = f"sqlite:///{SQLITE_PATH.as_posix()}"

def _create_engine_with_fallback(url: str):
    try:
        engine = create_engine(url, echo=SQL_ECHO, pool_pre_ping=True)
        # 立即验证一次连接（若是MySQL等网络库，及早发现错误）
        with engine.connect() as conn:
            conn.execute(sa_text("SELECT 1"))
        return engine
    except Exception as e:
        if FALLBACK_TO_SQLITE:
            # 可选：启用时才回退（默认关闭）
            fallback_engine = create_engine(SQLITE_URL, echo=SQL_ECHO, connect_args={"check_same_thread": False})
            return fallback_engine
        # 严格模式：直接抛出错误，阻止应用继续运行
        raise RuntimeError(
            f"数据库连接失败：{e}. 已禁用本地 SQLite 回退，请确认 MySQL 环境与环境变量配置正确。"
        )

engine = _create_engine_with_fallback(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 创建所有表的函数
from app.models.models import User

def create_tables():
    Base.metadata.create_all(bind=engine)

# 在需要的地方导入 SessionLocal 获取数据库会话
