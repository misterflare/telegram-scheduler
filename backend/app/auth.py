from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.hash import bcrypt
from sqlmodel import Session, select
from .config import settings
from .database import get_session
from .models import User

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET = settings.JWT_SECRET

def get_password_hash(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.verify(password, password_hash)

async def create_access_token(sub: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode = {"sub": sub, "exp": expire}
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
