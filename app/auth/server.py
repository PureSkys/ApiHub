from fastapi import HTTPException
from sqlmodel import Session, select
from pwdlib import PasswordHash
from app.auth.model import UserCreateAndUpdate, UserModel
from app.sentence.model import SentenceUserConfigModel

password_hash = PasswordHash.recommended()


# 密码验证方法
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# 密码哈希方法
def get_password_hash(password):
    return password_hash.hash(password)


def create_user(session: Session, user: UserCreateAndUpdate):
    try:
        user_email = user.email
        statement = select(UserModel).where(UserModel.email == user_email)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        user.hashed_password = get_password_hash(user.hashed_password)
        user_dict = user.model_dump(exclude_unset=True)
        user_db = UserModel(**user_dict)
        session.add(user_db)
        session.flush()
        user_db_id = user_db.id
        # 这里初始化所有应用用户信息
        sentence_user_config_db = SentenceUserConfigModel(user_id=user_db_id)
        # 提交从表默认数据
        session.add(sentence_user_config_db)
        session.commit()
        session.refresh(user_db)
        return user_db
    except HTTPException:
        # 主动抛的业务异常（400），直接向上抛，不进500逻辑
        raise
    except Exception as e:
        session.rollback()
        print(f"创建用户失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建用户失败，请联系管理员！")
