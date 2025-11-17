from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .users import Users

class Roles(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    name: str = Field(max_length=255, unique=True)
    description: str = Field(max_length=255)

    user_role: List["Users"] = Relationship(back_populates="role")

