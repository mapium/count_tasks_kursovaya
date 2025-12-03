from pydantic  import BaseModel

from fastapi import Form
from sqlmodel import Field

from pydantic import BaseModel
from fastapi import Form

class DepartmentsCreateSchema(BaseModel):
    name: str
    description: str

    @classmethod
    def as_form(        cls,
        name: str = Form(..., description="Имя подразделения"),
        description: str = Form(..., description="Описание подразделения")    ):
        return cls(name=name, description=description)