from fastapi import HTTPException
from sqlmodel import Session, select
from app.sentence.model import (
    SentenceUpdateAndCreate,
    CategoryUpdateAndCreate,
    SentenceCategoryModel,
)


# 创建分类方法
def create_sentence_category(session: Session, category: CategoryUpdateAndCreate):
    try:
        category_dict = category.model_dump(exclude_unset=True)
        print(category_dict)
        category_db = SentenceCategoryModel(**category_dict)
        session.add(category_db)
        session.commit()
        session.refresh(category_db)
        return category_db
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# 删除分类方法
def delete_sentence_category(session: Session, _id: str):
    category_db = session.get(SentenceCategoryModel, _id)
    if not category_db:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category_db)
    session.commit()
    print(category_db)
    return {"msg": "分类删除成功", "category": category_db.model_dump()}


# 更新分类方法
def update_sentence_category(
    session: Session, _id: str, category_update: CategoryUpdateAndCreate
):
    try:
        category_db = session.get(SentenceCategoryModel, _id)
        if not category_db:
            raise HTTPException(status_code=404, detail="Category not found")
        category_dict = category_update.model_dump(exclude_unset=True)
        category_db.sqlmodel_update(category_dict)
        session.commit()
        session.refresh(category_db)
        return category_db
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# 查询分类方法
def get_sentence_category(session: Session):
    try:
        statement = select(SentenceCategoryModel)
        category_db = session.exec(statement).all()
        return category_db
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 获取句子的方法
def get_sentence(session: Session, category: str):
    pass


# 更新句子方法
def update_sentence(
    session: Session, uuid: str, sentence_update: SentenceUpdateAndCreate
):
    pass


# 删除指定句子方法
def delete_sentence(session: Session, uuid: str):
    pass


# 创建句子
def create_sentence(session: Session, sentence_create: SentenceUpdateAndCreate):
    pass
