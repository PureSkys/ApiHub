from fastapi import APIRouter, Body, status, Depends, HTTPException
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.user.model import UserResponse, UserCreateAndUpdate
from app.user.server import (
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.core.database import SessionDep
from typing import Annotated
from app.user.model import Token
from app.config import fastapi_config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

# 获取Jwt环境变量
ACCESS_TOKEN_EXPIRE_MINUTES = fastapi_config.ACCESS_TOKEN_EXPIRE_MINUTES
auth_router = APIRouter()


@auth_router.post(
    "/",
    summary="注册用户",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_route(session: SessionDep, user: UserCreateAndUpdate = Body(...)):
    result = create_user(session, user)
    return result


@auth_router.get("/me", summary="获取当前用户数据", response_model=UserResponse)
def get_users_me_route(session: SessionDep, token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(session, token)
    return current_user


@auth_router.post("/token", summary="颁发Token", response_model=Token)
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="当前用户未激活",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
