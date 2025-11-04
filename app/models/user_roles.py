from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .users_model import Users
    from .roles import Roles


class User_Roles(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    name: str = Field(max_length=255, unique=True)
    description: str = Field(max_length=255)

    user: "Users" = Relationship(back_populates="user_roles")
    role: "Roles" = Relationship(back_populates="user_roles")
