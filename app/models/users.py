from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .employee_models import Employees
    from .tasks import Tasks
    from .task_comments import TaskComments
    from .roles import Roles


class Users(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    username: str = Field(max_length=255, unique=True)
    password: str = Field(max_length=255)
    role_id: int = Field(foreign_key="roles.id", default=1)
    employees: List["Employees"] = Relationship(back_populates="user")
    created_tasks: List["Tasks"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "[Tasks.creator_id]"}
    )
    assigned_tasks: List["Tasks"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "[Tasks.assignee_id]"}
    )
    comments: List["TaskComments"] = Relationship(back_populates="author")
    role: "Roles" = Relationship(back_populates="user_role")



# self.id=id
# self.username=username
# self.password_hash=password_hash
# self.employee_id=employee_id
# self.create_at=create_at
# self.last_login=last_login