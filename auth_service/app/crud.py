# auth_service/app/crud.py
from sqlalchemy.orm import Session
from auth_service.app import models, sсhemas
from argon2 import PasswordHasher
from .messaging import send_message_to_orders_service  # Импортируем функцию отправки сообщений

# Инициализация аргон2 хэшера
ph = PasswordHasher()

def create_user(db: Session, user: sсhemas.UserCreate):
    """
    Создание нового пользователя и отправка сообщения в очередь RabbitMQ для сервиса заказов.
    """
    hashed_password = ph.hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Отправка сообщения в сервис заказов с user_id
    send_message_to_orders_service(db_user.id)

    return db_user

def get_user_by_username(db: Session, username: str):
    """
    Получение пользователя по имени.
    """
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """
    Получение пользователя по ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()
