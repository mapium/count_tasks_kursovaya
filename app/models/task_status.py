from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from .tasks import Tasks

class Task_Status(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    name: str = Field(max_length=255)
    order_index: int = Field(default=0)

    tasks: List["Tasks"] = Relationship(back_populates="status")