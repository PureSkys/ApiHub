from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.user.route import auth_router
from app.core.database import init_db, close_db
from app.sentence.route import sentence_route
from app.core.health import health_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield
    close_db()


app = FastAPI(
    title="ApiHub",
    description="我的API聚合中心",
    lifespan=lifespan,
    version="1.0.0",
)
# 配置跨域中间件
# 允许所有跨域的核心配置
origins = ["*"]  # "*" 表示允许所有来源

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的来源列表，设置为["*"]表示所有来源
    allow_credentials=True,  # 允许携带Cookie等凭证
    allow_methods=["*"],  # 允许所有HTTP方法（GET、POST、PUT、DELETE等）
    allow_headers=["*"],  # 允许所有请求头
)
app.include_router(sentence_route, prefix="/sentence", tags=["Sentence"])
app.include_router(auth_router, prefix="/user", tags=["Auth"])
app.include_router(health_router, prefix="/health", tags=["Health"])
