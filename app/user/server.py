import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError
from sqlmodel import Session, select
from pwdlib import PasswordHash
from app.user.model import UserCreateAndUpdate, UserModel, TokenData
from app.sentence.model import SentenceUserConfigModel
from datetime import datetime, timedelta, timezone
from app.config import fastapi_config

password_hash = PasswordHash.recommended()

# 一个假的哈希值
DUMMY_HASH = password_hash.hash("DUMMY_HASH_vnVoKIj501AlSSBhmH4SZA752RAi4N7VF4")

# 获取环境变量的JWT配置
SECRET_KEY = fastapi_config.JWT_SECRET_KEY
ALGORITHM = fastapi_config.ALGORITHM


# 密码验证方法
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# 密码哈希方法
def get_password_hash(password):
    return password_hash.hash(password)


# 用户账号密码登录认证方法(通过验证返回用户信息)
def authenticate_user(session: Session, email: str, password: str):
    statement = select(UserModel).where(UserModel.email == email)
    user = session.exec(statement).first()
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# 创建token方法
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 解密token方法
def encode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# 创建用户方法
def create_user(session: Session, user: UserCreateAndUpdate):
    try:
        user_email = user.email
        statement = select(UserModel).where(UserModel.email == user_email)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        user.hashed_password = get_password_hash(user.hashed_password)
        user_dict = user.model_dump(exclude_unset=True)
        user_db = UserModel(**user_dict)
        session.add(user_db)
        session.flush()
        user_db_id = user_db.id
        # 这里初始化所有应用用户信息
        sentence_user_config_db = SentenceUserConfigModel(user_id=user_db_id)
        # 提交从表默认数据
        session.add(sentence_user_config_db)
        session.commit()
        session.refresh(user_db)
        return user_db
    except HTTPException:
        # 主动抛的业务异常（400），直接向上抛，不进500逻辑
        raise
    except Exception as e:
        session.rollback()
        print(f"创建用户失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建用户失败，请联系管理员！")


# 获取用户信息
def get_user(session: Session, user_id: str):
    user_db = session.get(UserModel, user_id)
    if user_db:
        return user_db
    return None


# 获取自己的用户信息方法
def get_current_user(session: Session, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = encode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, user_id=token_data.id)
    if user is None:
        raise credentials_exception
    return user
