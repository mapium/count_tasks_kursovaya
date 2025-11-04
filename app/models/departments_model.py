from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .employee_models import Employees
    from .tasks import Tasks


class Departments(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    employees: List["Employees"] = Relationship(back_populates="department")
    tasks: List["Tasks"] = Relationship(back_populates="department")