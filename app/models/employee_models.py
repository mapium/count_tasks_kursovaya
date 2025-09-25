from typing import Optional
from decimal import Decimal
from datetime import date
from sqlmodel import SQLModel, Field

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