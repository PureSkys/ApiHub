from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, func, Relationship
import uuid
from datetime import datetime
from pydantic import field_validator


# 数据库句子类型表模型
class SentenceCategoryModel(SQLModel, table=True):
    __tablename__ = "sentence_category"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    category: str = Field(description="句子分类", unique=True, index=True)
    description: str | None = Field(description="句子分类描述", default=None)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )
    sentences: list["SentenceContentModel"] = Relationship(
        back_populates="category", cascade_delete=True
    )


# 数据库句子内容表模型
class SentenceContentModel(SQLModel, table=True):
    __tablename__ = "sentence_content"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    is_disabled: bool = Field(description="句子状态", default=True)
    content: str = Field(description="句子内容", unique=True, index=True)
    from_source: str | None = Field(description="句子来源", default=None)
    from_who: str | None = Field(description="句子作者", default=None)
    likes: int = Field(description="句子喜欢数", default=0, ge=0)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )
    category_id: uuid.UUID = Field(foreign_key="sentence_category.id")
    category: SentenceCategoryModel = Relationship(back_populates="sentences")
    sentence_user_id: uuid.UUID = Field(foreign_key="sentence_user_config.id")
    sentence_user: "SentenceUserConfigModel" = Relationship(back_populates="sentences")


# 句子集用户权限模型
class SentenceUserConfigModel(SQLModel, table=True):
    __tablename__ = "sentence_user_config"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    is_superuser: bool = Field(default=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True)
    user: "UserModel" = Relationship(back_populates="sentence_user_config")
    sentences: list["SentenceContentModel"] = Relationship(
        back_populates="sentence_user",
        cascade_delete=True,
    )


# 分类创建/更新入参模型
class CategoryUpdateAndCreate(SQLModel):
    category: str
    description: str | None = None

    # 清洗category字段方法
    @field_validator("category")
    def clean_category(cls, v):
        cleaned_v = v.strip()
        if not cleaned_v:
            raise ValueError("分类名称不能为空（仅空格也不允许）")
        return cleaned_v


# 分类响应模型
class CategoryResponse(SQLModel):
    id: uuid.UUID
    category: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


# 句子创建/更新入参模型
class SentenceUpdateAndCreate(SQLModel):
    category_id: uuid.UUID  # 关联分类的UUID
    is_disabled: bool = True
    content: str
    from_source: str | None = None
    from_who: str | None = None
    likes: int | None = 0


# 句子响应模型（包含分类信息）
class SentenceResponse(SQLModel):
    id: uuid.UUID
    is_disabled: bool
    content: str
    from_source: str | None = None
    from_who: str | None = None
    likes: int
    created_at: datetime
    updated_at: datetime
    category_id: uuid.UUID


from app.user.model import UserModel
