from fastapi import HTTPException
from sqlmodel import Session

from app.auth.model import UserCreateAndUpdate, UserModel
from app.sentence.model import SentenceUserConfigModel


def create_user(session: Session, user: UserCreateAndUpdate):
    try:
        user_dict = user.model_dump(exclude_unset=True)
        user_db = UserModel(**user_dict)
        session.add(user_db)
        session.flush()
        user_db_id = user_db.id
        # 这里初始化所有应用用户信息
        sentence_user_config_db = SentenceUserConfigModel(user_id=user_db_id)

        session.add(sentence_user_config_db)
        session.commit()
        session.refresh(user_db)
        return user_db
    except Exception as e:
        session.rollback()
        print(f"创建用户失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建用户失败，请联系管理员！")
