from datetime import timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import select, Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.core.security import create_access_token, decode_token, admin_required
from app.db.session import get_session
from app.models.users import Users
from app.models.departments_model import Departments
from app.schemas.user_schema import UserSchema, UserSchemaCreate, UserSchemaCreateAsAdmin, UserLogin
from dotenv import load_dotenv
import os
ph=PasswordHasher()

load_dotenv()

def registration(data:UserSchemaCreate=Depends(UserSchemaCreate.as_form),session: Session = Depends(get_session)):
    """ Добавление """
    try:
        
        obj = Users(**data.dict(exclude_unset=True))
        obj.password=ph.hash(data.password)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except InterruptedError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Ошибка: дубликат или нарушение целостности данных")
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")


def admin_registration(data: UserSchemaCreateAsAdmin, user: Users = Depends(admin_required), session: Session = Depends(get_session)):
    """ Добавление пользователя администратором """
    try:
        # Проверка: если роль менеджера (role_id == 2), проверяем количество менеджеров
        if data.role_id == 2:
            # Получаем количество подразделений
            departments_count = session.exec(select(func.count(Departments.id))).one()
            
            # Получаем количество существующих менеджеров
            managers_count = session.exec(select(func.count(Users.id)).where(Users.role_id == 2)).one()
            
            # Проверяем, не превышает ли количество менеджеров количество подразделений
            if managers_count >= departments_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Невозможно добавить менеджера: количество менеджеров ({managers_count}) не должно превышать количество подразделений ({departments_count})"
                )
        
        obj = Users(
            username=data.username,
            password=ph.hash(data.password),
            role_id=data.role_id
        )
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except HTTPException:
        raise
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Ошибка: дубликат или нарушение целостности данных")
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def login(
    form_data: UserLogin,
    session: Session = Depends(get_session)):
    """     Авторизация      """
    user = session.exec(select(Users).where(Users.username == form_data.username)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    try:
        ph.verify(user.password, form_data.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


from jose import jwt, JWTError

def refresh_access_token(refresh_token: str):
    """Генерация нового токена"""
    username = decode_token(refresh_token)
    if not username:
        raise HTTPException(status_code=401, detail="невалидный токен")

    new_access_token = create_access_token(
        data={"sub": username, "type": "access"},
        expires_delta=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))),
    )
    return new_access_token


def get_users(user: Users = Depends(admin_required),session: Session = Depends(get_session), page: int = 1, size: int = 10) -> Page[Users]:
    " Вывод информации о пользователях """
    try:
        sql = select(Users)
        return paginate(session, sql)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Внутренняя ошибка сервера: {str(e)}")


