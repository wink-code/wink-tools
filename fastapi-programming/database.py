from sqlalchemy import create_engine, Column, Integer, Float, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./factory.db"
# 创建引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False})
# 创建会话(用于操作数据库)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 基类
Base = declarative_base()
# 定义设备数据模型
class Device(Base):
    __tablename__ = "device"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, index=True)
    name = Column(String(50))
    field = Column(String(40))
    value = Column(Float)
    status = Column(String(20))
    update_time = Column(String(50))

# 创建表
Base.metadata.create_all(bind=engine)
