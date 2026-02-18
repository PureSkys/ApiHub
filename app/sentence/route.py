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
    category_db = server.create_sentence_category(session, category, token)
    return category_db


@sentence_route.delete(
    "/category/{_id}", summary="删除分类路由", status_code=status.HTTP_200_OK
)
def delete_sentence_category_route(
    session: SessionDep, _id: uuid.UUID, token: str = Depends(oauth2_scheme)
):
    result = server.delete_sentence_category(session, _id, token)
    return result


# todo更新时重复项检测要避开自身，因为有时修改的是分类描述而不是分类名称
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
    result = server.update_sentence_category(session, _id, category_update, token)
    return result


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
    description="可以通过数组批量创建",
    status_code=status.HTTP_201_CREATED,
)
def create_sentence_route(
    session: SessionDep,
    sentence_create: SentenceUpdateAndCreate | list[SentenceUpdateAndCreate],
    token: str = Depends(oauth2_scheme),
):
    sentence = server.create_sentence(session, sentence_create, token)
    return sentence


@sentence_route.delete(
    "/{_id}",
    summary="删除句子路由",
    status_code=status.HTTP_200_OK,
)
def delete_sentence_route(
    session: SessionDep, _id: uuid.UUID, token: str = Depends(oauth2_scheme)
):
    result = server.delete_sentence(session, _id, token)
    return result


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
    sentence = server.update_sentence(session, _id, sentence_update, token)
    return sentence


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
