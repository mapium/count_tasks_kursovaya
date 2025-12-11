from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from app.models.tasks import Tasks
from app.models.departments_model import Departments


class TaskCreate(BaseModel):
    """Схема для создания задачи без id и автоматических полей"""
    title: str
    description: str
    creator_id: int
    assignee_id: int
    department_id: int
    status_id: int
    priority: str = "малый"
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None


class DepartmentTasksGroup(BaseModel):
    """Схема для группы задач по отделу"""
    department_id: int
    department_name: str
    tasks: List[Tasks]


class TasksGroupedByDepartment(BaseModel):
    """Схема для сгруппированных задач по отделам"""
    departments: List[DepartmentTasksGroup]


class TaskStatusUpdate(BaseModel):
    """Схема для изменения статуса задачи по названию"""
    status_name: str


class TaskCommentCreate(BaseModel):
    """Схема для создания комментария к задаче"""
    comment_text: str
class GetTaskSchema(BaseModel):
    """Схема для получения задачи"""
    id: int
    title: str
    description: str
    creator: str
    assignee: str
    department: str
    status: str
    priority: str
    planned_start_date: date
    planned_end_date: date

