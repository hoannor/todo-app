from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.models import User
from src.service import get_db

# thiet lap cau hinh JWT

SECRET_KEY = "hoan7203"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

# ham mat khau
def get_password_hash(password: str):
    return pwd_context.hash(password)

# ham kiem tra mat khau
def vertify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# tao token truy cap
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

# lay nguoi dung to co so du lieu
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# xac thuc nguoi dung
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not vertify_password(password, user.hashed_password):
        return False
    return user

# xac thuc va lay thong tin nguoi dung tu token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credeentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate credentials", headers = {"WWW-Authenticate": "Bearer"}, )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credeentials_exception
    except JWTError:
        raise credeentials_exception
    user = get_user(db, username = username)
    if user is None:
        raise credeentials_exception
    return user