from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 请根据你的实际 MySQL 配置修改以下内容
MYSQL_USER = 'root'
MYSQL_PASSWORD = '111111'
MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'
MYSQL_DB = 'yhywf'

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 创建所有表的函数
from app.models.models import User

def create_tables():
    Base.metadata.create_all(bind=engine)

# 在需要的地方导入 SessionLocal 获取数据库会话
