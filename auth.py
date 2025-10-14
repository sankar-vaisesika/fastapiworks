from jose import JWTError,jwt

from fastapi import HTTPException,status,Depends

from sqlmodel import Session,select

from models import User 

from database import get_session

from passlib.context import CryptContext

from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
import bcrypt

config = bcrypt.gensalt()

SECRET_KEY="123454477463543"

ALGORITHM="HS256"

ACCESS_TOKEN_EXPIRE_MINUTES=60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_password_hash(password: str) -> str:
    # bcrypt accepts up to 72 bytes. Ensure it's encoded safely.
    # password = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password.encode('utf-8'), config)
    # print("DEBUG: Password length =", len(password))
    # return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = session.exec(select(User).where(User.username == username)).first()
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")