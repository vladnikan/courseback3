from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL вашей базы данных PostgreSQL
DATABASE_URL = "postgresql://postgres:1@localhost:5432/order_service_db"

# Настройка движка SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создание фабрики для сессий базы данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
