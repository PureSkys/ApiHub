import uuid
from typing import Annotated
from fastapi import APIRouter, status, Query, Depends, Request
from pydantic import BaseModel

from app.sentence.model import (
    SentenceResponse,
    SentenceUpdateAndCreate,
    CategoryResponse,
    CategoryUpdateAndCreate,
)
from app.core.database import SessionDep
import app.sentence.server as server
from app.user.route import oauth2_scheme

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
    summary="创建句子路由（批量和单个都行）",
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
    summary="单个删除句子路由",
    status_code=status.HTTP_200_OK,
)
def delete_sentence_route(
    session: SessionDep, _id: uuid.UUID, token: str = Depends(oauth2_scheme)
):
    result = server.delete_sentence(session, _id, token)
    return result


@sentence_route.put(
    "/{_id}",
    summary="单个更新句子路由",
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
    summary="随机句子路由",
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


@sentence_route.get(
    "/admin/paginated",
    summary="分页查询句子路由（支持筛选）",
    status_code=status.HTTP_200_OK,
)
def get_sentence_paginated_route(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: str = Query(None, description="模糊搜索句子内容"),
    category_id: str = Query(
        None, description="分类ID，传入'all'或不传入则查询所有分类"
    ),
    is_disabled: bool = Query(None, description="句子状态，true为禁用，false为启用"),
    token: str = Depends(oauth2_scheme),
):
    result = server.get_sentence_paginated(
        session, page, page_size, token, search, category_id, is_disabled
    )
    return result


# 批量更新句子状态请求模型
class BatchUpdateStatusRequest(BaseModel):
    ids: list[uuid.UUID]
    is_disabled: bool


@sentence_route.post(
    "/admin/batch/status",
    summary="批量更新句子状态路由",
    status_code=status.HTTP_200_OK,
)
def batch_update_sentence_status_route(
    session: SessionDep,
    request: BatchUpdateStatusRequest,
    token: str = Depends(oauth2_scheme),
):
    result = server.batch_update_sentence_status(
        session, request.ids, request.is_disabled, token
    )
    return result


# 批量删除句子请求模型
class BatchDeleteRequest(BaseModel):
    ids: list[uuid.UUID]


@sentence_route.post(
    "/admin/batch/delete",
    summary="批量删除句子路由",
    status_code=status.HTTP_200_OK,
)
def batch_delete_sentences_route(
    session: SessionDep,
    request: BatchDeleteRequest,
    token: str = Depends(oauth2_scheme),
):
    result = server.batch_delete_sentences(session, request.ids, token)
    return result


@sentence_route.get(
    "/admin/stats",
    summary="获取应用统计信息路由",
    status_code=status.HTTP_200_OK,
)
def get_sentence_stats_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
):
    result = server.get_sentence_stats(session, token)
    return result


@sentence_route.post(
    "/like/{sentence_id}",
    summary="点赞路由",
    status_code=status.HTTP_200_OK,
)
def like_sentence_route(
    session: SessionDep,
    sentence_id: uuid.UUID,
    request: Request,
):
    # 获取用户IP地址
    client_ip = request.client.host
    result = server.like_sentence(session, sentence_id, client_ip)
    return result


@sentence_route.post(
    "/unlike/{sentence_id}",
    summary="取消点赞路由",
    status_code=status.HTTP_200_OK,
)
def unlike_sentence_route(
    session: SessionDep,
    sentence_id: uuid.UUID,
    request: Request,
):
    # 获取用户IP地址
    client_ip = request.client.host
    result = server.unlike_sentence(session, sentence_id, client_ip)
    return result
