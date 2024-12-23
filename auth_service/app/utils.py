# Файл: auth_service/app/utils.py
import jwt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from auth_service.app import database
from auth_service.app.models import User

# Настройки для работы с JWT
SECRET_KEY = 'secret'  # Секретный ключ для кодирования и декодирования токенов
ALGORITHM = 'HS256'  # Алгоритм для подписи JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время жизни токена (по умолчанию)

# Схема для извлечения токена из заголовков запросов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

# Настройка хэширования паролей
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


# Хэширование пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Функция для создания токена доступа
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=300)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# Функция для декодирования токена
def decode_token(token: str):
    """
    Расшифровка JWT токена.
    """
    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Извлекаем поле 'sub', которое используется как идентификатор пользователя
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: 'sub' is missing")

        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Получение текущего пользователя из токена
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    username = decode_token(token)  # Используем decode_token вместо decode_access_token
    if not username:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    # Поиск пользователя в базе данных
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user



# Аутентификация пользователя по имени и паролю
def authenticate_user(username: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user
