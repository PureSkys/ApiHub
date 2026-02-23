from sqlmodel import create_engine, Session, select, SQLModel

from app.user.model import UserModel, UserCreateAndUpdate
from app.user.server import create_user
from app.config import fastapi_config
from fastapi import Depends
from typing import Annotated

# 如果使用SQLMODEL创建数据库表请在这里导入所有的模型
from app.sentence import model as sentence_model
from app.user import model as auth_model
from app.school import model as school_model

_ = (sentence_model, auth_model, school_model)

engine = create_engine(
    str(fastapi_config.SQLMODEL_DATABASE_URI),
    pool_pre_ping=True,
)


def _get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(_get_session)]


def init_db():
    try:
        with Session(engine) as session:
            SQLModel.metadata.create_all(engine)  # 开发环境可以使用该行代码初始化数据库

            statement = select(UserModel)
            users = session.exec(statement).all()
            user_count = len(users)
            if user_count == 0:
                user_db = UserCreateAndUpdate(
                    email=fastapi_config.FIRST_SUPERUSER,
                    hashed_password=fastapi_config.FIRST_SUPERUSER_PASSWORD,
                    nickname="超级管理员",
                )
                user_sup = create_user(session, user_db)
                user_sup.is_superuser = True
                user_sup.active = True
                session.add(user_sup)
                session.commit()
            print("🚀 数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败：{e}")


def close_db():
    try:
        engine.dispose()
        print("✅ 数据库引擎已处置，连接池所有连接已关闭")
    except Exception as e:
        print(f"❌ 关闭数据库资源时出错：{e}")
