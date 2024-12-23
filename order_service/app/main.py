import asyncio
import requests
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, utils, database
from .database import SessionLocal, engine
from .utils import oauth2_scheme
from order_service.app.messaging import listen_for_orders
from auth_service.app import models as auth_models
from order_service.app.utils import decode_token
from order_service.app.models import Order  # Импорт модели Order

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Зависимость для получения сессии базы данных
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Асинхронный запуск прослушивания сообщений
@app.on_event("startup")
async def startup():
    print("Starting to listen for messages from RabbitMQ...")
    asyncio.create_task(listen_for_orders())  # Запуск в фоне, чтобы не блокировать основной поток

# Зависимость для проверки токена и получения данных о пользователе
async def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Извлекаем пользователя по токену
        user = utils.get_user_from_token(token, db)  # Новый способ получения пользователя
        return user  # Возвращаем пользователя
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# URL сервиса авторизации
AUTH_SERVICE_URL = "http://127.0.0.1:8000"  # URL вашего `auth_service`

def get_user_from_auth_service(user_id: int):
    """Получает данные пользователя из auth_service."""
    response = requests.get(f"{AUTH_SERVICE_URL}/users/{user_id}")
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="User not found")

@app.get("/orders/")
def get_user_orders(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Раскодируем JWT и получаем данные пользователя
    user_data = decode_token(token)
    user_id = user_data["sub"]

    # Получаем информацию о пользователе из auth_service
    user_info = get_user_from_auth_service(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    # Запрашиваем заказы пользователя из локальной базы данных
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return {"user": user_info, "orders": orders}

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db=db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.get("/orders/user/{user_id}", response_model=List[schemas.OrderResponse])
def read_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    db_orders = crud.get_orders_by_user(db=db, user_id=user_id)
    return db_orders


@app.post("/neworder/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    Создание нового заказа.
    """
    db_order = crud.create_order(db=db, order=order)
    return db_order

# @app.post("/place_order/")
# def place_order(user: auth_models.User = Depends(verify_token)):
#     """
#     Оформление заказа для авторизованного пользователя.
#     """
#     return {"message": "Order placed successfully"}

@app.get("/orders2/")
async def get_orders(token: str = Depends(oauth2_scheme)):
    print(f"Received token: {token}")
    user = decode_token(token)
    return {"orders": [], "user": user}
