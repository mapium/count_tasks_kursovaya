from datetime import timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.core.security import create_access_token, decode_token, admin_required, get_current_user
from app.db.session import get_session
from app.models.users import Users
from app.schemas.user_schema import (
    UserSchema,
    UserSchemaCreate,
    UserSchemaCreateAsAdmin,
    UserLogin,
    UserUpdateAsAdmin,
    UserPasswordChange,
)
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
    """Возвращает список пользователей с пагинацией.
    Доступно только администратору.
    """
    try:
        sql = select(Users)
        return paginate(session, sql)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Внутренняя ошибка сервера: {str(e)}")


def update_user_by_admin(
    user_id: int,
    data: UserUpdateAsAdmin,
    current_user: Users = Depends(admin_required),
    session: Session = Depends(get_session),
) -> Users:
    """Обновляет данные пользователя по ID от имени администратора.
    Поддерживает смену роли и необязательную смену пароля.
    """
    try:
        user = session.get(Users, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

        user.username = data.username
        user.role_id = data.role_id
        if data.password:
            user.password = ph.hash(data.password)

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except HTTPException:
        raise
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка: дубликат или нарушение целостности данных",
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )


def delete_user_by_admin(
    user_id: int,
    current_user: Users = Depends(admin_required),
    session: Session = Depends(get_session),
):
    """Удаляет пользователя по ID от имени администратора.
    Запрещает удаление текущего авторизованного администратора.
    """
    try:
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить текущего администратора",
            )

        user = session.get(Users, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

        session.delete(user)
        session.commit()
        return {"detail": "Пользователь удален"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )


def change_my_password(
    data: UserPasswordChange,
    current_user: Users = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Изменяет пароль текущего авторизованного пользователя.
    Проверяет старый пароль и минимальную длину нового.
    """
    try:
        if not data.new_password or len(data.new_password.strip()) < 4:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Новый пароль должен содержать минимум 4 символа",
            )

        try:
            ph.verify(current_user.password, data.old_password)
        except VerifyMismatchError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Старый пароль указан неверно",
            )

        current_user.password = ph.hash(data.new_password)
        session.add(current_user)
        session.commit()
        return {"detail": "Пароль успешно изменен"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )


