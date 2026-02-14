import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select, func
from app.sentence.model import (
    SentenceUpdateAndCreate,
    CategoryUpdateAndCreate,
    SentenceCategoryModel,
    SentenceContentModel,
)
from app.user import server as user_server


# 获取基础信息方法
def get_basic_info(session: Session, token: str):
    user_info = user_server.get_current_user(session, token)
    sentence_user_is_superuser = user_info.sentence_user_config.is_superuser
    user_is_superuser = user_info.is_superuser
    sentence_user_sentence_content = user_info.sentence_user_config.sentences
    sentence_user_id = user_info.sentence_user_config.id
    return (
        sentence_user_is_superuser,
        user_is_superuser,
        sentence_user_id,
        sentence_user_sentence_content,
    )


# 创建分类方法
def create_sentence_category(
    session: Session, category: CategoryUpdateAndCreate, token: str
):
    (sentence_user_is_superuser, user_is_superuser, *_) = get_basic_info(session, token)
    if sentence_user_is_superuser or user_is_superuser:
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

            category_db = SentenceCategoryModel(
                **category.model_dump(exclude_unset=True)
            )
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
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")


# 删除分类方法
def delete_sentence_category(session: Session, _id: uuid.UUID, token: str):
    (sentence_user_is_superuser, user_is_superuser, *_) = get_basic_info(session, token)
    if sentence_user_is_superuser or user_is_superuser:
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
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")


# 更新分类方法
def update_sentence_category(
    session: Session,
    _id: uuid.UUID,
    category_update: CategoryUpdateAndCreate,
    token: str,
):
    (sentence_user_is_superuser, user_is_superuser, *_) = get_basic_info(session, token)
    if sentence_user_is_superuser or user_is_superuser:
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
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")


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


def create_sentence(
    session: Session,
    sentence_create: SentenceUpdateAndCreate | list[SentenceUpdateAndCreate],
    token: str,
):
    # 获取用户基础信息
    (sentence_user_is_superuser, user_is_superuser, sentence_user_id, *_) = (
        get_basic_info(session, token)
    )
    # 判断是否为超级用户，用于设置is_disabled属性
    is_superuser = sentence_user_is_superuser or user_is_superuser
    # 统一转为列表处理，简化逻辑
    if not isinstance(sentence_create, list):
        sentence_creates = [sentence_create]
        is_single = True
    else:
        sentence_creates = sentence_create
        is_single = False
    # 存储要创建的句子对象
    sentence_objects = []
    try:
        # 第一步：提取所有待创建的句子内容
        contents = [item.content for item in sentence_creates]
        # 检查1：待创建列表内部是否有重复内容
        content_count = {}
        for content in contents:
            content_count[content] = content_count.get(content, 0) + 1
        # 找出列表内重复的内容
        internal_duplicates = [
            content for content, count in content_count.items() if count > 1
        ]
        if internal_duplicates:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"待创建列表中句子「{', '.join(internal_duplicates)}」重复，无法创建！",
            )
        # 检查2：检查数据库中已存在的内容
        statement = select(SentenceContentModel.content).where(
            SentenceContentModel.content.in_(contents)
        )
        # 正确获取查询结果中的内容字符串
        existing_contents = []
        for row in session.exec(statement).all():
            # 兼容不同SQLAlchemy版本的返回格式（可能是元组或单个值）
            if isinstance(row, (tuple, list)):
                existing_contents.append(row[0])
            else:
                existing_contents.append(row)
        # 转换为集合提高查询效率
        existing_contents_set = set(existing_contents)
        # 找出和数据库重复的内容
        db_duplicates = [
            content for content in contents if content in existing_contents_set
        ]
        if db_duplicates:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"句子「{', '.join(db_duplicates)}」已存在于数据库中，无法重复创建！",
            )
        # 第二步：处理每个句子对象
        for item in sentence_creates:
            # 设置权限相关字段
            item.is_disabled = False if is_superuser else True
            # 初始化点赞数
            item.likes = 0
            # 转换为字典并创建数据库模型对象
            sentence_dict = item.model_dump(exclude_unset=True)
            sentence_db = SentenceContentModel(
                **sentence_dict, sentence_user_id=sentence_user_id
            )
            sentence_objects.append(sentence_db)
        # 第三步：批量添加并提交
        session.add_all(sentence_objects)
        session.commit()
        # 刷新所有对象以获取数据库生成的字段（如id）
        for obj in sentence_objects:
            session.refresh(obj)
        # 根据输入类型返回对应结果
        return sentence_objects[0] if is_single else sentence_objects
    except HTTPException:
        # 主动抛出的HTTP异常直接向上传递
        raise
    except Exception as e:
        # 其他异常回滚事务并返回通用错误
        session.rollback()
        print(f"创建句子失败：{str(e)}")
        raise HTTPException(status_code=400, detail="创建句子失败，请联系管理员！")


# 删除句子方法
def delete_sentence(session: Session, _id: uuid.UUID, token: str):
    (
        sentence_user_is_superuser,
        user_is_superuser,
        *_,
        sentence_user_sentence_content,
    ) = get_basic_info(session, token)
    try:
        sentence_db = session.get(SentenceContentModel, _id)
        if not sentence_db:
            raise HTTPException(status_code=404, detail="Sentence not found")
        if (sentence_user_is_superuser or user_is_superuser) or (
            sentence_db in sentence_user_sentence_content
        ):
            session.delete(sentence_db)
            session.commit()
            return {"msg": "句子删除成功", "category": sentence_db.model_dump()}
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除句子失败：{str(e)}")
        raise HTTPException(status_code=422, detail="删除句子失败，请联系管理员！")


# 更新句子方法
def update_sentence(
    session: Session,
    _id: uuid.UUID,
    sentence_update: SentenceUpdateAndCreate,
    token: str,
):
    (
        sentence_user_is_superuser,
        user_is_superuser,
        *_,
        sentence_user_sentence_content,
    ) = get_basic_info(session, token)
    try:
        sentence_db = session.get(SentenceContentModel, _id)
        if not sentence_db:
            raise HTTPException(status_code=404, detail="Sentence not found")
        if (sentence_user_is_superuser or user_is_superuser) or (
            sentence_db in sentence_user_sentence_content
        ):
            sentence_dict = sentence_update.model_dump(exclude_unset=True)
            sentence_db.sqlmodel_update(sentence_dict)
            session.commit()
            session.refresh(sentence_db)
            return sentence_db
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")
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
