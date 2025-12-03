from typing import TYPE_CHECKING, List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone, date
if TYPE_CHECKING:
    from .users import Users
    from .departments_model import Departments
    from .task_status import Task_Status
    from .task_comments import TaskComments


class Tasks(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    title: str = Field(max_length=255)
    description: str = Field(max_length=255)
    creator_id: int = Field(foreign_key="users.id")
    assignee_id: int = Field(foreign_key="users.id")
    department_id: int = Field(foreign_key="departments.id")
    status_id: int = Field(foreign_key="task_status.id")
    priority: str = Field(max_length=10, default="малый")
    planned_start_date: date = Field(default=None)
    planned_end_date: date = Field(default=None)
    actual_start_date: Optional[date] = Field(default=None)
    actual_end_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    creator: "Users" = Relationship(back_populates="created_tasks", sa_relationship_kwargs={"foreign_keys": "[Tasks.creator_id]"})
    assignee: "Users" = Relationship(back_populates="assigned_tasks", sa_relationship_kwargs={"foreign_keys": "[Tasks.assignee_id]"})
    department: "Departments" = Relationship(back_populates="tasks")
    status: "Task_Status" = Relationship(back_populates="tasks")
    comments: List["TaskComments"] = Relationship(back_populates="task")