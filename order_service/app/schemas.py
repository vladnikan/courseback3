from pydantic import BaseModel
from typing import List
from datetime import datetime

# Схема для элементов заказа
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        orm_mode = True


# Схема для создания заказа
class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]

    class Config:
        orm_mode = True


# Схема для отображения заказа
class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemCreate]

    class Config:
        orm_mode = True
