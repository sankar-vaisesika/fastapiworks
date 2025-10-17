from jose import JWTError, jwt         # Handling JWTs (encoding, decoding, and error management).
from fastapi import HTTPException, status, Depends  # FastAPI core utilities for raising exceptions, HTTP status codes, and dependency injection.
from sqlmodel import Session, select   # Database interaction (querying the User model).
from models import User                # User model to check credentials
from database import get_session       # get DB session
from passlib.context import CryptContext  # built-in password hashing utilities
from datetime import datetime, timedelta # for token expiry management
from fastapi.security import OAuth2PasswordBearer  # token-based authentication system
from dotenv import load_dotenv
import os

# -------------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------------
load_dotenv() #reads .env file


# -------------------------------
# CONFIGURATION CONSTANTS
# -------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")      # Secret key to sign JWT tokens
ALGORITHM =  os.getenv("ALGORITHM", "HS256")                   # Hashing algorithm for JWT (HS256 = HMAC-SHA256)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))      # Token expires after 60 minutes

# -------------------------------
# PASSWORD HASHING CONFIG
# -------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# bcrypt salt (used to add randomness to hashing)
# config = bcrypt.gensalt()  

# -------------------------------
# PASSWORD UTILS
# -------------------------------
def get_password_hash(password: str) -> str:
    """
    Hash a plain password securely using passlib (bcrypt).
    Truncate password to 72 bytes to avoid bcrypt limit.
    """
    #convert to bytes and truncate to 72 bytes    
    # safe_password = password.encode("utf-8")[:72]
    # return bcrypt.hashpw(password.encode('utf-8'), config)
    # print("DEBUG: Password length =", len(password))
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    """Verify if the provided plain password matches the stored hash.
    Truncate to 72 bytes to match hashing truncation.
    """
    # safe_plain = plain.encode("utf-8")[:72]

    return pwd_context.verify(plain, hashed)

# -------------------------------
# JWT (JSON Web Token) UTILS
# -------------------------------
def create_access_token(data: dict):
    """
    Create a JWT access token containing user data. 
    Automatically sets the expiration time.
    """

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    """
    Decode the JWT token and return the current user.
    Raises an exception if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = session.exec(select(User).where(User.username == username)).first()
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")     