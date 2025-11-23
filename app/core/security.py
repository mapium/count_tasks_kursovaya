import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer


from fastapi.responses import JSONResponse

from sqlmodel import select, text
from sqlalchemy import inspect
from starlette import status

from app.db.session import get_session
from app.models.users import Users
from app.models.roles import Roles
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


load_dotenv()  # загрузка переменных из .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def decode_token(token:str):
    """
    Декодирует JWT токен и возвращает имя пользователя
    :param token: JWT токен
    :return: username (sub) или None
    """
    try:
        # Декодирование токена и проверка  подписи и срока её действия
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return  payload.get("sub") #Извлекает поле "sub" (обычно username)
    except JWTError:
        return None


def get_current_user(token:str=Depends(oauth2_scheme), session=Depends(get_session))-> Users :
    """
    Получение объекта пользователя по токену
    :param token: токен из запроса (передаётся автоматически с помощью Depends и OAuth2PasswordBearer)
    :param session: сессия для базы данных (вызывается  при помощи Depends)
    :return: объект User или исключение HTTPException 401
    """
    username=decode_token(token)
    if not username:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Невалидный токен")
    user=session.exec(select(Users).where(Users.username==username )).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Пользователь не найден")
    return user



def create_access_token(data:dict,expires_delta: timedelta=None):
    """    Создаёт JWT access-токен с данными и временем жизни
    :param data: словарь с данными для кодирования в токен (например, {"sub": username})
    :param expires_delta: timedelta - время действия токена
    :return: JWT строка
    """
    to_encode=data.copy()  #Копирует переданные данные
    # Добавление в них времени истечения срока действия (exp) — обязательное поле JWT
    expire=datetime.utcnow()+(expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    #Возвращает закодированный JWT токен с использованием секретного ключа и алгоритма
    # jose автоматически конвертирует datetime в timestamp при кодировании
    return jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)


def admin_required(user: Users = Depends(get_current_user), session=Depends(get_session)):
    """
    Проверка роли администратора
    :param user: Объект класса Users
    :param session: сессия для базы данных
    :return: объект Users или исключение HTTPException 403
    """
    if user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return user

def department_manager_required(user: Users = Depends(get_current_user), session=Depends(get_session)):
    """
    Проверка роли Руководителя отдела
    :param user: Объект класса Users
    :param session: сессия для базы данных
    :return: объект Users или исключение HTTPException 403
    """
    if user.role_id != 2 and user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права руководителя отдела/администратора"
        )
    return user