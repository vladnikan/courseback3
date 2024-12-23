# auth_service/app/main.py
from fastapi.middleware.cors import CORSMiddleware
import asyncio  # Импортируем asyncio
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from auth_service.app import models, sсhemas, crud
from auth_service.app.database import SessionLocal, engine
from auth_service.app import utils  # Импортируем утилиты для проверки пароля
from auth_service.app.messaging import send_message_to_orders_service  # Импортируем функцию для отправки сообщения
from fastapi.security import OAuth2PasswordRequestForm
from auth_service.app.utils import create_access_token
from auth_service.app.models import User

# Создание таблиц в базе данных
models.Base.metadata.create_all(bind=engine)

# Инициализация приложения FastAPI
app = FastAPI()

SECRET_TOKEN = "your_secret_token"

# Настройка CORS
origins = [
    "http://127.0.0.1:8001",  # Ордер-сервис
    "http://localhost:8001",  # Для запросов через localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все HTTP-методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=sсhemas.UserResponse)
async def create_user(user: sсhemas.UserCreate, db: Session = Depends(get_db)):
    """
    Создание нового пользователя и отправка сообщения в очередь RabbitMQ для сервиса заказов.
    """
    db_user = crud.create_user(db=db, user=user)

    # Отправка сообщения в RabbitMQ
    asyncio.create_task(send_message_to_orders_service(user_id=db_user.id))  # Вызываем асинхронную функцию для отправки сообщения

    return db_user


# Эндпоинт для логина
@app.post("/login/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Логин и получение токена.
    """
    # Ищем пользователя в базе данных по имени пользователя
    db_user = crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user or not utils.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Если пользователь найден и пароль совпадает, создаем токен
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username}

# @app.post("/login/")
# def login(user: sсhemas.UserLogin, db: Session = Depends(get_db)):
#     # Получаем пользователя по имени
#     db_user = crud.get_user_by_username(db=db, username=user.username)
#     if not db_user or not utils.verify_password(user.password, db_user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
#     # Создание JWT токена
#     token = utils.create_access_token(data={"sub": db_user.username})
#     return {"access_token": token, "token_type": "bearer"}


# @app.post("/login/")
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):
#     # Получаем пользователя из базы данных
#     db_user = crud.get_user_by_username(db=db, username=form_data.username)
#     if not db_user or not utils.verify_password(form_data.password, db_user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     # Создание токена
#     token = utils.create_access_token(data={"sub": db_user.username})
#     return {"access_token": token, "token_type": "bearer"}

# @app.post("/login/")
# def login(user: sсhemas.UserLogin, db: Session = Depends(get_db)):
#     """
#     Логика для авторизации пользователя.
#     """
#     db_user = crud.get_user_by_username(db=db, username=user.username)
#     if db_user and utils.verify_password(user.password, db_user.password):  # Используем utils.verify_password
#         # Генерация JWT токена
#         token = utils.create_access_token(data={"username": user.username})
#         return {"access_token": token, "token_type": "bearer"}
#     raise HTTPException(status_code=401, detail="Invalid credentials")
