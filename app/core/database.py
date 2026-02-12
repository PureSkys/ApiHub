from sqlmodel import SQLModel, create_engine, Session
from app.config import fastapi_config
from fastapi import Depends
from typing import Annotated

# 如果使用SQLMODEL创建数据库表请在这里导入所有的模型
from app.sentence import model as sentence_model

_ = sentence_model

engine = create_engine(
    str(fastapi_config.SQLMODEL_DATABASE_URI),
    pool_pre_ping=True,
)


def init_db():
    try:
        SQLModel.metadata.create_all(engine)
        print("🚀 数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败：{e}")


def _get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(_get_session)]


def close_db():
    try:
        engine.dispose()
        print("✅ 数据库引擎已处置，连接池所有连接已关闭")
    except Exception as e:
        print(f"❌ 关闭数据库资源时出错：{e}")
