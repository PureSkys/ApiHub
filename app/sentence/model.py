from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, func, Relationship
import uuid
from datetime import datetime
from pydantic import field_validator


# 数据库句子类型表模型
class SentenceCategoryModel(SQLModel, table=True):
    __tablename__ = "sentence_category"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7,
        primary_key=True,
        index=True,
    )
    # 句子分类字段
    category: str = Field(..., nullable=False, unique=True, index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime, default=func.now(), nullable=False, onupdate=func.now()
        )
    )
    sentences: list["SentenceContentModel"] = Relationship(
        back_populates="category", passive_deletes=True
    )


# 数据库句子内容表模型
class SentenceContentModel(SQLModel, table=True):
    __tablename__ = "sentence_content"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7,
        primary_key=True,
        index=True,
    )
    # 句子内容
    content: str = Field(..., nullable=False, unique=True, index=True)
    # 句子来源
    from_source: str | None = Field(default=None, nullable=True)
    # 句子作者
    from_who: str | None = Field(default=None, nullable=True)
    # 句子喜欢数
    likes: int = Field(default=0, nullable=False)
    # 创建时间
    created_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), nullable=False)
    )
    # 更新时间
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime, default=func.now(), nullable=False, onupdate=func.now()
        )
    )
    category_id: uuid.UUID = Field(
        foreign_key="sentence_category.id", nullable=False, ondelete="CASCADE"
    )
    category: SentenceCategoryModel = Relationship(back_populates="sentences")


# 分类创建/更新入参模型
class CategoryUpdateAndCreate(SQLModel):
    category: str

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
    created_at: datetime
    updated_at: datetime


# 句子创建/更新入参模型
class SentenceUpdateAndCreate(SQLModel):
    category_id: uuid.UUID  # 关联分类的UUID
    content: str
    from_source: str | None = None
    from_who: str | None = None
    likes: int | None = 0


# 句子响应模型（包含分类信息）
class SentenceResponse(SQLModel):
    id: uuid.UUID
    content: str
    from_source: str | None = None
    from_who: str | None = None
    likes: int
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse
