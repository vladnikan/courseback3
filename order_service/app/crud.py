import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy.sql import func


from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from . import models, schemas

# Простая функция для создания заказа
def create_order(db: Session, order: schemas.OrderCreate):
    """
    Создание нового заказа с товарами.
    """
    # Проверяем наличие пользователя через API
    user_response = requests.get(f'http://127.0.0.1:8000/users/{order.user_id}')
    if user_response.status_code != 200:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_response.json()  # Получаем данные пользователя

    # Суммируем стоимость товаров в заказе
    total_price = sum(item.price * item.quantity for item in order.items)

    # Создаем заказ
    db_order = models.Order(
        user_id=order.user_id,
        total_price=total_price,
        status="pending",
        created_at=func.now(),
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Добавление товаров в заказ
    for item in order.items:
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
        )
        db.add(db_order_item)

    db.commit()

    # Возвращаем заказ с товарами
    return db_order




def get_order(db: Session, order_id: int):
    """
    Получение заказа по ID с товарными позициями.
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        # Получаем все товары, связанные с заказом
        order_items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        order.items = order_items  # Связываем товары с заказом
    return order

def get_orders_by_user(db: Session, user_id: int):
    """
    Получение всех заказов пользователя с товарными позициями.
    """
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
    for order in orders:
        # Добавляем товары в каждый заказ
        order_items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        order.items = order_items
    return orders



