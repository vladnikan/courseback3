from typing import List  # Для типизации
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from . import crud, models, schemas  # Убедитесь, что ваши файлы правильно названы
from .database import get_db  # Для работы с базой данных

router = APIRouter()


# @router.post("/orders/", response_model=schemas.OrderResponse)
# def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
#     """
#     Создание нового заказа.
#     """
#     db_order = crud.create_order(db=db, order=order)
#     return db_order


@router.get("/users/{user_id}/orders", response_model=List[schemas.OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """
    Получение всех заказов конкретного пользователя.
    """
    orders = crud.get_orders_by_user_id(db=db, user_id=user_id)
    if not orders:
        raise HTTPException(status_code=404, detail="Orders not found")
    return orders


@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о конкретном заказе по его ID.
    """
    order = crud.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
