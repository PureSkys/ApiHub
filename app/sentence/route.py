import uuid
from fastapi import APIRouter, status, Body, Path, Query
from app.sentence.model import (
    SentenceResponse,
    SentenceUpdateAndCreate,
    CategoryResponse,
    CategoryUpdateAndCreate,
)
from app.core.database import SessionDep
import app.sentence.server as server

sentence_route = APIRouter()


@sentence_route.post(
    "/category",
    summary="创建分类路由",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sentence_category_route(
    session: SessionDep,
    category: CategoryUpdateAndCreate = Body(...),
):
    category_db = server.create_sentence_category(session, category)
    return category_db


@sentence_route.delete(
    "/category/{_id}", summary="删除分类路由", status_code=status.HTTP_200_OK
)
def delete_sentence_category_route(session: SessionDep, _id: uuid.UUID = Path(...)):
    result = server.delete_sentence_category(session, _id)
    return result


@sentence_route.put(
    "/category/{_id}",
    summary="更新分类路由",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
def update_sentence_category_route(
    session: SessionDep,
    _id: uuid.UUID = Path(...),
    category_update: CategoryUpdateAndCreate = Body(...),
):
    result = server.update_sentence_category(session, _id, category_update)
    return result


@sentence_route.get(
    "/category}",
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
    session: SessionDep, sentence_create: SentenceUpdateAndCreate = Body(...)
):
    sentence = server.create_sentence(session, sentence_create)
    return sentence


@sentence_route.delete(
    "/{_id}",
    summary="删除句子路由",
    status_code=status.HTTP_200_OK,
)
def delete_sentence_route(session: SessionDep, _id: uuid.UUID = Path(...)):
    result = server.delete_sentence(session, _id)
    return result


@sentence_route.put(
    "/{_id}",
    summary="更新句子路由",
    response_model=SentenceResponse,
    status_code=status.HTTP_200_OK,
)
def update_sentence_route(
    session: SessionDep,
    _id: uuid.UUID = Path(...),
    sentence_update: SentenceUpdateAndCreate = Body(...),
):
    sentence = server.update_sentence(session, _id, sentence_update)
    return sentence


@sentence_route.get(
    "/{category_id}",
    summary="查询句子路由",
    response_model=list[SentenceResponse],
    status_code=status.HTTP_200_OK,
)
def get_sentence_route(
    session: SessionDep,
    category_id: str = Path(...),
    limit: int = Query(10, ge=1, le=20),
):
    sentences = server.get_sentence(session, category_id, limit)
    return sentences
