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
            # 只有当分类名发生变化时，才检查是否与其他分类重复（不包含自身）
            if category_db.category != category_update.category:
                statement = select(SentenceCategoryModel).where(
                    SentenceCategoryModel.category == category_update.category,
                    SentenceCategoryModel.id != _id,  # 排除自身
                )
                existing_category = session.exec(statement).first()
                if existing_category:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"分类「{category_update.category}」已存在，无法重复创建！",
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


# 创建句子方法
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
    else:
        sentence_creates = sentence_create
    # 存储处理结果
    result = {
        "success_count": 0,
        "internal_duplicates": [],
        "db_duplicates": [],
    }
    # 存储要创建的句子对象
    sentence_objects = []
    try:
        # 第一步：去除数组内重复的content，仅保留一个
        unique_content_items = {}
        for item in sentence_creates:
            if item.content not in unique_content_items:
                unique_content_items[item.content] = item
            else:
                result["internal_duplicates"].append(item.content)
        # 获取去重后的内容列表
        unique_items = list(unique_content_items.values())
        # 提取所有待创建的句子内容
        contents = [item.content for item in unique_items]

        # 检查数据库中已存在的内容
        if contents:
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
            result["db_duplicates"] = db_duplicates

            # 过滤出数据库中不存在的内容
            non_duplicate_items = [
                item
                for item in unique_items
                if item.content not in existing_contents_set
            ]
        else:
            non_duplicate_items = []

        # 第二步：处理每个不重复的句子对象
        for item in non_duplicate_items:
            # 设置权限相关字段
            if not is_superuser:
                item.is_disabled = True
            # 初始化点赞数
            item.likes = 0
            # 转换为字典并创建数据库模型对象
            sentence_dict = item.model_dump(exclude_unset=True)
            sentence_db = SentenceContentModel(
                **sentence_dict, sentence_user_id=sentence_user_id
            )
            sentence_objects.append(sentence_db)

        # 第三步：批量添加并提交
        if sentence_objects:
            session.add_all(sentence_objects)
            session.commit()
            # 刷新所有对象以获取数据库生成的字段（如id）
            for obj in sentence_objects:
                session.refresh(obj)
            result["success_count"] = len(sentence_objects)

        # 返回处理结果
        return result
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


# 获取随机句子的方法
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


# 分页查询句子的方法
def get_sentence_paginated(session: Session, page: int, page_size: int, token: str, category_id: str = None):
    try:
        # 获取用户权限信息
        (sentence_user_is_superuser, user_is_superuser, sentence_user_id, *_) = get_basic_info(session, token)
        
        # 构建查询语句
        if sentence_user_is_superuser or user_is_superuser:
            # 超级管理员可以查看所有句子
            statement = select(SentenceContentModel)
        else:
            # 普通用户只能查看自己的句子
            statement = select(SentenceContentModel).where(
                SentenceContentModel.sentence_user_id == sentence_user_id
            )
        
        # 如果提供了分类id，则添加分类过滤
        if category_id and category_id != "all":
            statement = statement.where(SentenceContentModel.category_id == category_id)
        
        # 计算总条数
        total_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(total_statement).one()
        
        # 计算偏移量并添加排序
        offset = (page - 1) * page_size
        statement = statement.order_by(SentenceContentModel.created_at.desc()).offset(offset).limit(page_size)
        
        # 执行查询
        sentences = session.exec(statement).all()
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        # 返回分页结果
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": sentences
        }
    except Exception as e:
        session.rollback()
        print(f"分页查询句子失败：{str(e)}")
        raise HTTPException(status_code=500, detail="分页查询句子失败，请联系管理员！")