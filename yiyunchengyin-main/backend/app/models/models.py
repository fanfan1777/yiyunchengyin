from app.models.db import Base  # 导入Base
from sqlalchemy import Column, Integer, String, DateTime
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# 可在此文件继续添加其他模型
