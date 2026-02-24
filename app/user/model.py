import uuid
from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.sentence.model import SentenceUserConfigModel
    from app.school.model import SchoolAdminModel


class UserModel(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid7,
        primary_key=True,
        index=True,
        unique=True,
    )
    email: EmailStr = Field(
        description="用户邮箱地址，用于登录和身份识别",
        unique=True,
        max_length=255,
    )
    hashed_password: str = Field(description="用户密码的哈希值")
    nickname: str | None = Field(
        description="用户昵称，显示名称",
        default=None,
        max_length=8,
    )
    active: bool = Field(
        description="用户激活状态，True表示已激活可正常使用",
        default=False,
    )
    is_superuser: bool = Field(
        description="超级管理员标识，True表示拥有系统最高权限",
        default=False,
    )
    sentence_user_config: "SentenceUserConfigModel" = Relationship(
        back_populates="user",
        cascade_delete=True,
    )
    school_admin: "SchoolAdminModel" = Relationship(
        back_populates="user",
        cascade_delete=True,
    )


class Token(BaseModel):
    access_token: str = Field(description="JWT访问令牌")
    token_type: str = Field(description="令牌类型，通常为bearer")


class TokenData(BaseModel):
    id: str | None = Field(description="用户ID", default=None)


class UserResponse(SQLModel):
    id: uuid.UUID = Field(description="用户唯一标识符")
    email: EmailStr = Field(description="用户邮箱地址")
    nickname: str | None = Field(description="用户昵称")
    active: bool = Field(description="用户激活状态")


class UserCreateAndUpdate(SQLModel):
    email: EmailStr = Field(description="用户邮箱地址")
    hashed_password: str = Field(description="用户密码（明文，系统会自动哈希）")
    nickname: str | None = Field(
        description="用户昵称，可选，最多8个字符",
        default=None,
    )
