from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field

class Users(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    username: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)



# self.id=id
# self.username=username
# self.password_hash=password_hash
# self.employee_id=employee_id
# self.create_at=create_at
# self.last_login=last_login