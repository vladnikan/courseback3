from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from auth_service.app.models import User

#ForeignKey("users.id")
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Исправлено на 'users.id'
    total_price = Column(Float, default=0.0)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, default=0.0, nullable=False)

    order = relationship("Order", back_populates="items")
