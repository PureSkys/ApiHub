from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.auth.route import auth_router
from app.core.database import init_db, close_db
from app.sentence.route import sentence_route


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # 若使用Alembic管理数据库请注销init_db()
    # init_db()
    yield
    close_db()


app = FastAPI(
    title="ApiHub",
    description="我的API聚合中心",
    lifespan=lifespan,
)

app.include_router(sentence_route, prefix="/sentence", tags=["Sentence"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
