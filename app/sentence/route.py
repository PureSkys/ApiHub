from fastapi import APIRouter, status, Body, Path
from enum import Enum
from app.sentence.model import (
    SentenceResponse,
    SentenceUpdateAndCreate,
    CategoryResponse,
    CategoryUpdateAndCreate,
)
from app.core.database import SessionDep
import app.sentence.server as server

sentence_route = APIRouter()


class SENTENCE_CATEGORY(str, Enum):
    动画 = "动画"
    漫画 = "漫画"
    游戏 = "游戏"
    文学 = "文学"
    原创 = "原创"
    网络 = "网络"
    其他 = "其他"
    影视 = "影视"
    诗词 = "诗词"
    网易云 = "网易云"
    哲学 = "哲学"
    抖机灵 = "抖机灵"
    全部 = "全部"


@sentence_route.post(
    "/category",
    summary="创建分类路由",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sentence_category_route(
    session: SessionDep, category: CategoryUpdateAndCreate
):
    category_db = server.create_sentence_category(session, category)
    return category_db


@sentence_route.delete(
    "/category/{_id}", summary="删除分类路由", status_code=status.HTTP_200_OK
)
def delete_sentence_category_route(session: SessionDep, _id: str = Path(...)):
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
    _id: str = Path(...),
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


# TODO:句子内容相关路由
@sentence_route.post(
    "/",
    summary="创建句子路由",
    response_model=SentenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sentence_route(
    session: SessionDep, sentence_create: SentenceUpdateAndCreate
):
    sentence = server.create_sentence(session, sentence_create)
    return sentence


@sentence_route.delete(
    "/{uuid}",
    summary="删除句子路由",
    status_code=status.HTTP_200_OK,
)
def delete_sentence_route(session: SessionDep, uuid: str = Path(...)):
    result = server.delete_sentence(session, uuid)
    return result


@sentence_route.put(
    "/{uuid}",
    summary="更新句子路由",
    response_model=SentenceResponse,
    status_code=status.HTTP_200_OK,
)
def update_sentence_route(
    session: SessionDep,
    uuid: str = Path(...),
    sentence_update: SentenceUpdateAndCreate = Body(...),
):
    sentence = server.update_sentence(session, uuid, sentence_update)
    return sentence


@sentence_route.get(
    "/{category}",
    summary="查询句子路由",
    response_model=list[SentenceResponse],
    status_code=status.HTTP_200_OK,
)
def get_sentence_route(session: SessionDep, category: SENTENCE_CATEGORY):
    sentences = server.get_sentence(session, category)
    return sentences
