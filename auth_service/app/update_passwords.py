from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from auth_service.app.models import User

# Настройка хэширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка подключения к БД
DATABASE_URL = "postgresql://postgres:1@localhost:5432/auth_service_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Обновление паролей в базе
users = session.query(User).all()
for user in users:
    if not user.password.startswith("$2b$"):  # Проверка, не хэширован ли пароль уже
        user.password = pwd_context.hash(user.password)
        session.add(user)

session.commit()
print("Passwords updated successfully!")
