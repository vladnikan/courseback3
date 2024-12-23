from jose import JWTError, jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from auth_service.app import models as auth_models
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = 'secret'  # Должен совпадать с ключом в auth_service
ALGORITHM = "HS256"

# Для работы с OAuth2 схемой
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/login")

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Это словарь
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_from_token(token: str, db: Session) -> auth_models.User:
    """
    Извлекаем пользователя из базы данных по токену.
    """
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=403, detail="Invalid token or user_id not found")

    # Находим пользователя по имени (или user_id, в зависимости от того, что ты решил использовать)
    user = db.query(auth_models.User).filter(auth_models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=403, detail="User not found")

    return user
