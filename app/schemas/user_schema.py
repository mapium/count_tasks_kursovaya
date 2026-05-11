from pydantic  import BaseModel

from fastapi import Form
from sqlmodel import Field

from pydantic import BaseModel
from fastapi import Form

class UserSchema(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(        cls,
        username: str = Form(..., description="Имя пользователя"),
        password: str = Form(..., description="Пароль")    ):
        """Создает схему пользователя из form-данных.
        Используется в эндпоинтах с multipart/form-data.
        """
        return cls(username=username, password=password)

class UserSchemaCreate(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(        cls,
        username: str = Form(..., description="Имя пользователя"),
        password: str = Form(..., description="Пароль"),   
        ):
        """Создает схему регистрации из form-данных.
        Нормализует вход для FastAPI Depends.
        """
        return cls(username=username, password=password)

class UserSchemaCreateAsAdmin(BaseModel):
    username: str
    password: str
    role_id: int

    @classmethod
    def as_form(cls,
        username: str = Form(..., description="Имя пользователя"),
        password: str = Form(..., description="Пароль"),
        role_id: int = Form(..., description="ID роли")):
        """Создает схему админ-регистрации из form-данных.
        Включает явную передачу роли пользователя.
        """
        return cls(username=username, password=password, role_id=role_id)

class UserLogin(BaseModel):
    username: str
    password: str
    @classmethod
    def as_form(cls,
        username: str = Form(..., description="Имя пользователя"),
        password: str = Form(..., description="Пароль")):
        """Создает схему входа из form-данных.
        Используется при авторизации пользователя.
        """
        return cls(username=username, password=password)


class UserUpdateAsAdmin(BaseModel):
    username: str
    password: str | None = None
    role_id: int

    @classmethod
    def as_form(
        cls,
        username: str = Form(..., description="Имя пользователя"),
        password: str = Form("", description="Новый пароль (необязательно)"),
        role_id: int = Form(..., description="ID роли"),
    ):
        """Создает схему обновления пользователя администратором.
        Пустой пароль преобразуется в None.
        """
        normalized_password = password.strip() if isinstance(password, str) else ""
        return cls(
            username=username,
            password=normalized_password or None,
            role_id=role_id,
        )


class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str

    @classmethod
    def as_form(
        cls,
        old_password: str = Form(..., description="Старый пароль"),
        new_password: str = Form(..., description="Новый пароль"),
    ):
        """Создает схему смены пароля из form-данных.
        Проверка корректности выполняется в контроллере.
        """
        return cls(old_password=old_password, new_password=new_password)