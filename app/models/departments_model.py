from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy.orm import foreign
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .employee_models import Employees
    from .tasks import Tasks
    from .users import Users


class Departments(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    department_manager_id: Optional[int] = Field(foreign_key="users.id", default=None)

    employees: List["Employees"] = Relationship(back_populates="department")
    tasks: List["Tasks"] = Relationship(back_populates="department")
    manager: "Users" = Relationship(sa_relationship_kwargs={"foreign_keys": "[Departments.department_manager_id]"})