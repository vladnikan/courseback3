from .database import get_db  # убедитесь, что get_db настроено для подключения к базе
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth_service.app.utils import create_access_token
from auth_service.app import crud, database, sсhemas

router = APIRouter()


@router.post("/users/")
def create_user(user: sсhemas.UserCreate, db: Session = Depends(get_db)):
    # Проверка существования пользователя по username
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Создание нового пользователя
    return crud.create_user(db=db, user=user)
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время жизни токена

router = APIRouter()
