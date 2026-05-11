from typing import Optional

from fastapi import Form
from pydantic import BaseModel

class DepartmentsCreateSchema(BaseModel):
    name: str
    description: str
    department_manager_id: Optional[int] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., description="Имя подразделения"),
        description: str = Form(..., description="Описание подразделения"),
        department_manager_id: Optional[int] = Form(None, description="ID менеджера подразделения"),
    ):
        """Создает схему подразделения из form-данных.
        Поддерживает необязательную привязку менеджера.
        """
        return cls(
            name=name,
            description=description,
            department_manager_id=department_manager_id,
        )