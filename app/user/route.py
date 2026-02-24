from fastapi import APIRouter, Body, status, Depends, HTTPException
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.user.model import UserResponse, UserCreateAndUpdate, Token
from app.user.server import (
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.core.database import SessionDep
from typing import Annotated
from app.config import fastapi_config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

ACCESS_TOKEN_EXPIRE_MINUTES = fastapi_config.ACCESS_TOKEN_EXPIRE_MINUTES
auth_router = APIRouter()


@auth_router.post(
    "/",
    summary="注册新用户",
    description="创建一个新的用户账户。用户创建后默认为未激活状态，需要管理员激活后才能正常使用。",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "用户创建成功",
            "content": {
                "application/json": {
                    "example": {
                        "id": "01234567-89ab-cdef-0123-456789abcdef",
                        "email": "user@example.com",
                        "nickname": "新用户",
                        "active": False,
                    }
                }
            },
        },
        400: {
            "description": "邮箱已被注册",
            "content": {
                "application/json": {"example": {"detail": "邮箱已被注册"}}
            },
        },
    },
)
def create_user_route(
    session: SessionDep,
    user: UserCreateAndUpdate = Body(
        ...,
        description="用户注册信息",
        examples=[
            {
                "email": "newuser@example.com",
                "hashed_password": "mypassword123",
                "nickname": "新用户",
            }
        ],
    ),
):
    result = create_user(session, user)
    return result


@auth_router.get(
    "/me",
    summary="获取当前用户信息",
    description="获取当前已登录用户的详细信息，需要提供有效的JWT令牌。",
    response_model=UserResponse,
    responses={
        200: {
            "description": "成功获取用户信息",
            "content": {
                "application/json": {
                    "example": {
                        "id": "01234567-89ab-cdef-0123-456789abcdef",
                        "email": "user@example.com",
                        "nickname": "用户昵称",
                        "active": True,
                    }
                }
            },
        },
        401: {
            "description": "未授权 - 令牌无效或已过期",
            "content": {
                "application/json": {"example": {"detail": "Could not validate credentials"}}
            },
        },
    },
)
def get_users_me_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
):
    current_user = get_current_user(session, token)
    return current_user


@auth_router.post(
    "/token",
    summary="用户登录获取令牌",
    description="使用邮箱和密码登录系统，成功后返回JWT访问令牌。令牌用于后续API请求的身份验证。",
    response_model=Token,
    responses={
        200: {
            "description": "登录成功，返回访问令牌",
            "content": {
                "application/json": {
                    "example": {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer"}
                }
            },
        },
        401: {
            "description": "认证失败 - 用户名或密码错误，或用户未激活",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "用户名或密码错误",
                            "value": {"detail": "用户名或密码错误"},
                        },
                        "inactive_user": {
                            "summary": "用户未激活",
                            "value": {"detail": "当前用户未激活"},
                        },
                    }
                }
            },
        },
    },
)
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
