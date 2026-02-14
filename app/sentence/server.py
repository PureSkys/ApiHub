import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select, func
from app.sentence.model import (
    SentenceUpdateAndCreate,
    CategoryUpdateAndCreate,
    SentenceCategoryModel,
    SentenceContentModel,
)


# 创建分类方法
def create_sentence_category(session: Session, category: CategoryUpdateAndCreate):
    try:
        statement = select(SentenceCategoryModel).where(
            SentenceCategoryModel.category == category.category
        )
        existing_category = session.exec(statement).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"分类「{category.category}」已存在，无法重复创建！",
            )

        category_db = SentenceCategoryModel(**category.model_dump(exclude_unset=True))
        session.add(category_db)
        session.commit()
        session.refresh(category_db)
        return category_db

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        if "unique constraint" in str(e).lower() and "name" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"分类「{category.category}」已存在，无法重复创建！",
            )
        print(f"创建分类失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建分类失败，请联系管理员！")


# 删除分类方法
def delete_sentence_category(session: Session, _id: uuid.UUID):
    try:
        category_db = session.get(SentenceCategoryModel, _id)
        if not category_db:
            raise HTTPException(status_code=404, detail="Category not found")
        session.delete(category_db)
        session.commit()
        return {"msg": "分类删除成功", "category": category_db.model_dump()}
    except Exception as e:
        session.rollback()
        print(f"删除分类失败：{str(e)}")
        raise HTTPException(status_code=422, detail="删除分类失败，请联系管理员！")


# 更新分类方法
def update_sentence_category(
    session: Session, _id: uuid.UUID, category_update: CategoryUpdateAndCreate
):
    try:
        category_db = session.get(SentenceCategoryModel, _id)
        if not category_db:
            raise HTTPException(status_code=404, detail="Category not found")
        if category_db.category == category_update.category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"分类「{category_db.category}」已存在，无法重复创建！",
            )
        category_dict = category_update.model_dump(exclude_unset=True)
        category_db.sqlmodel_update(category_dict)
        session.commit()
        session.refresh(category_db)
        return category_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新分类失败：{str(e)}")
        raise HTTPException(status_code=422, detail="更新分类失败，请联系管理员！")


# 查询分类方法
def get_sentence_category(session: Session):
    try:
        statement = select(SentenceCategoryModel)
        category_db = session.exec(statement).all()
        return category_db
    except Exception as e:
        session.rollback()
        print(f"查询分类失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询分类失败，请联系管理员！")


# 创建句子方法
def create_sentence(
    session: Session, sentence_create: SentenceUpdateAndCreate, sentence_user_id
):
    try:
        statement = select(SentenceContentModel).where(
            SentenceContentModel.content == sentence_create.content
        )
        sentence_db: SentenceContentModel = session.exec(statement).first()
        if sentence_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"句子「{sentence_db.content}」已存在，无法重复创建！",
            )
        sentence_dict = sentence_create.model_dump(exclude_unset=True)
        sentence_db = SentenceContentModel(
            **sentence_dict, sentence_user_id=sentence_user_id
        )
        session.add(sentence_db)
        session.commit()
        session.refresh(sentence_db)
        return sentence_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"创建句子失败：{str(e)}")
        raise HTTPException(status_code=400, detail="创建句子失败，请联系管理员！")


# 删除句子方法
def delete_sentence(session: Session, _id: uuid.UUID):
    try:
        sentence_db = session.get(SentenceContentModel, _id)
        if not sentence_db:
            raise HTTPException(status_code=404, detail="Sentence not found")
        session.delete(sentence_db)
        session.commit()
        return {"msg": "句子删除成功", "category": sentence_db.model_dump()}
    except Exception as e:
        session.rollback()
        print(f"删除句子失败：{str(e)}")
        raise HTTPException(status_code=422, detail="删除句子失败，请联系管理员！")


# 更新句子方法
def update_sentence(
    session: Session, _id: uuid.UUID, sentence_update: SentenceUpdateAndCreate
):
    try:
        sentence_db = session.get(SentenceContentModel, _id)
        if not sentence_db:
            raise HTTPException(status_code=404, detail="Sentence not found")
        sentence_dict = sentence_update.model_dump(exclude_unset=True)
        sentence_db.sqlmodel_update(sentence_dict)
        session.commit()
        session.refresh(sentence_db)
        return sentence_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新句子失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新句子失败，请联系管理员！")


# 获取句子的方法
def get_sentence(session: Session, category_id: str, limit: int):
    try:
        if category_id == "all":
            statement = (
                select(SentenceContentModel).order_by(func.random()).limit(limit)
            )
        else:
            statement = (
                select(SentenceContentModel)
                .where(SentenceContentModel.category_id == category_id)
                .order_by(func.random())
                .limit(limit)
            )
        sentences = session.exec(statement).all()
        return sentences
    except Exception as e:
        session.rollback()
        print(f"查询句子失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询句子失败，请联系管理员！")
