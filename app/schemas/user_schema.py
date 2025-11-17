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
        return cls(username=username, password=password)

class UserSchemaCreate(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(        cls,
        username: str = Form(..., description="Имя пользователя"),
        password: str = Form(..., description="Пароль"),   
        ):
        
        
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
        
        return cls(username=username, password=password, role_id=role_id)