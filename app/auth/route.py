from fastapi import APIRouter, Body, status

from app.auth.model import UserResponse, UserCreateAndUpdate
from app.auth.server import create_user
from app.core.database import SessionDep

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
