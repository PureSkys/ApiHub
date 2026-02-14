import uuid
from typing import Annotated
from fastapi import APIRouter, status, Query, Depends, HTTPException
from sqlmodel import select
from app.sentence.model import (
    SentenceResponse,
    SentenceUpdateAndCreate,
    CategoryResponse,
    CategoryUpdateAndCreate,
    SentenceContentModel,
)
from app.core.database import SessionDep
import app.sentence.server as server
from app.user.route import oauth2_scheme
from app.user import server as user_server

sentence_route = APIRouter()


@sentence_route.post(
    "/category",
    summary="创建分类路由",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sentence_category_route(
    session: SessionDep,
    category: CategoryUpdateAndCreate,
    token: str = Depends(oauth2_scheme),
):
    sentence_user_is_superuser = user_server.get_current_user(
        session, token
    ).sentence_user_config.is_superuser
    user_is_superuser = user_server.get_current_user(session, token).is_superuser
    if sentence_user_is_superuser or user_is_superuser:
        category_db = server.create_sentence_category(session, category)
        return category_db
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")


@sentence_route.delete(
    "/category/{_id}", summary="删除分类路由", status_code=status.HTTP_200_OK
)
def delete_sentence_category_route(
    session: SessionDep, _id: uuid.UUID, token: str = Depends(oauth2_scheme)
):
    sentence_user_is_superuser = user_server.get_current_user(
        session, token
    ).sentence_user_config.is_superuser
    user_is_superuser = user_server.get_current_user(session, token).is_superuser
    if sentence_user_is_superuser or user_is_superuser:
        result = server.delete_sentence_category(session, _id)
        return result
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")


@sentence_route.put(
    "/category/{_id}",
    summary="更新分类路由",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
def update_sentence_category_route(
    session: SessionDep,
    _id: uuid.UUID,
    category_update: CategoryUpdateAndCreate,
    token: str = Depends(oauth2_scheme),
):
    sentence_user_is_superuser = user_server.get_current_user(
        session, token
    ).sentence_user_config.is_superuser
    user_is_superuser = user_server.get_current_user(session, token).is_superuser
    if sentence_user_is_superuser or user_is_superuser:
        result = server.update_sentence_category(session, _id, category_update)
        return result
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")


@sentence_route.get(
    "/category",
    summary="查询分类路由",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
)
def get_sentence_category_route(session: SessionDep):
    result = server.get_sentence_category(session)
    return result


@sentence_route.post(
    "/",
    summary="创建句子路由",
    response_model=SentenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sentence_route(
    session: SessionDep,
    sentence_create: SentenceUpdateAndCreate,
    token: str = Depends(oauth2_scheme),
):
    sentence_user_is_superuser = user_server.get_current_user(
        session, token
    ).sentence_user_config.is_superuser
    user_is_superuser = user_server.get_current_user(session, token).is_superuser
    sentence_user_id = user_server.get_current_user(
        session, token
    ).sentence_user_config.id
    if sentence_user_is_superuser or user_is_superuser:
        sentence_create.is_disabled = False
    sentence_create.likes = 0
    sentence = server.create_sentence(session, sentence_create, sentence_user_id)
    return sentence


@sentence_route.delete(
    "/{_id}",
    summary="删除句子路由",
    status_code=status.HTTP_200_OK,
)
def delete_sentence_route(
    session: SessionDep, _id: uuid.UUID, token: str = Depends(oauth2_scheme)
):
    user_info = user_server.get_current_user(session, token)
    sentence_user_is_superuser = user_info.sentence_user_config.is_superuser
    user_is_superuser = user_info.is_superuser
    sentence_user_sentence_content = user_info.sentence_user_config.sentences
    statement = select(SentenceContentModel).where(SentenceContentModel.id == _id)
    sentence_db = session.exec(statement).first()
    if sentence_user_is_superuser or user_is_superuser:
        result = server.delete_sentence(session, _id)
        return result
    elif sentence_db in sentence_user_sentence_content:
        result = server.delete_sentence(session, _id)
        return result
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")


@sentence_route.put(
    "/{_id}",
    summary="更新句子路由",
    response_model=SentenceResponse,
    status_code=status.HTTP_200_OK,
)
def update_sentence_route(
    session: SessionDep,
    _id: uuid.UUID,
    sentence_update: SentenceUpdateAndCreate,
    token: str = Depends(oauth2_scheme),
):
    user_info = user_server.get_current_user(session, token)
    sentence_user_is_superuser = user_info.sentence_user_config.is_superuser
    user_is_superuser = user_info.is_superuser
    sentence_user_sentence_content = user_info.sentence_user_config.sentences
    statement = select(SentenceContentModel).where(SentenceContentModel.id == _id)
    sentence_db = session.exec(statement).first()
    if sentence_user_is_superuser or user_is_superuser:
        sentence = server.update_sentence(session, _id, sentence_update)
        return sentence
    elif sentence_db in sentence_user_sentence_content:
        sentence = server.update_sentence(session, _id, sentence_update)
        return sentence
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="操作被禁止")


@sentence_route.get(
    "/{category_id}",
    summary="查询句子路由",
    response_model=list[SentenceResponse],
    status_code=status.HTTP_200_OK,
)
def get_sentence_route(
    session: SessionDep,
    category_id: str,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    sentences = server.get_sentence(session, category_id, limit)
    return sentences
