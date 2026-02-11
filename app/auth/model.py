import uuid

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


# 用户数据模型
class UserModel(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid7,
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
    )
    email: EmailStr = Field(description="用户邮箱", nullable=False, unique=True)
    hashed_password: str = Field(description="用户密码", nullable=False)
    nickname: str | None = Field(description="用户昵称", nullable=True)
    active: bool = Field(description="用户状态", nullable=False, default=False)
    sentence_user_config: "SentenceUserConfigModel" = Relationship(
        back_populates="user"
    )


# 用户响应模型
class UserResponse(SQLModel):
    id: uuid.UUID
    email: EmailStr
    nickname: str | None
    active: bool


# 用户创建和更新模型
class UserCreateAndUpdate(SQLModel):
    email: EmailStr
    hashed_password: str
    nickname: str | None
    active: bool = Field(default=False)


from app.sentence.model import SentenceUserConfigModel
