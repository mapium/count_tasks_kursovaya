from typing import Optional
from decimal import Decimal
from datetime import date
from sqlmodel import SQLModel, Field

class Departments(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = None