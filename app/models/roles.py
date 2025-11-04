from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user_roles import User_Roles

class Roles(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    name: str = Field(max_length=255, unique=True)
    description: str = Field(max_length=255)

    user_roles: List["User_Roles"] = Relationship(back_populates="role")

