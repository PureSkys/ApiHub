import uuid
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field, Relationship


# 用户数据模型
class UserModel(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    email: EmailStr = Field(description="用户邮箱", unique=True, max_length=255)
    hashed_password: str = Field(description="用户密码")
    nickname: str | None = Field(description="用户昵称", default=None, max_length=8)
    active: bool = Field(description="用户状态", default=False)
    is_superuser: bool = Field(description="超级管理员状态", default=False)
    # 下面关联项目内其他应用的模型
    sentence_user_config: "SentenceUserConfigModel" = Relationship(
        back_populates="user",
        cascade_delete=True,
    )


# Token模型(返回给前端)
class Token(BaseModel):
    access_token: str
    token_type: str


# Token内的负载 sub
class TokenData(BaseModel):
    id: str | None = None


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
    nickname: str | None = Field(default=None)


from app.sentence.model import SentenceUserConfigModel
