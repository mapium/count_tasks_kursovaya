from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from app.models.departments_model import Departments
from app.models.users_model import Users


class Employees(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    middle_name: Optional[str] = Field(default=None, max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=12)
    email: str = Field(max_length=255)
    passport_data: str = Field(max_length=10)
    inn: Optional[str] = Field(default=None, max_length=12)
    snils: Optional[str] = Field(default=None, max_length=11)
    department_id: int = Field(foreign_key="departments.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    department: Departments = Relationship(back_populates="employees")
    user: Optional[Users] = Relationship(back_populates="employees")