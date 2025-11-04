from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from .tasks import Tasks
    from .users_model import Users

class TaskComments(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    task_id: int = Field(foreign_key="tasks.id")
    author_id: int = Field(foreign_key="users.id")
    comment_text: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    task: "Tasks" = Relationship(back_populates="comments")
    author: "Users" = Relationship(back_populates="comments")