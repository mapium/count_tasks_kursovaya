from fastapi import APIRouter, Depends
from sqlmodel import Session
from fastapi_pagination import Page
from app.core.security import admin_required
from app.db.session import get_session
from app.controllers.departments_controller import get_all_departments, get_department_by_id, post_department, delete_department, put_department
from app.models import Users
from app.models.departments_model import Departments
from app.schemas.departments_schema import DepartmentsCreateSchema


router = APIRouter() 

@router.get("/departments", tags=["Подразделения"], response_model=Page[Departments])
def список_подразделений(session: Session = Depends(get_session)):
    return get_all_departments(session)

@router.get("/departments/{id}", tags=["Подразделения"])
def подразделение_по_идентификатору(id: int, session: Session = Depends(get_session)):
    return get_department_by_id(id, session)

@router.post("/departments", tags=["Подразделения"], description="Только с правами администратора")
def создание_подразделения(employee: DepartmentsCreateSchema, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return post_department(employee, session)

@router.put("/departments/{id}", tags=["Подразделения"], description="Только с правами администратора")
def изменить_подразделение(id: int, data: DepartmentsCreateSchema, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return put_department(id, data, session)

@router.delete("/departments/{id}", tags=["Подразделения"], description="Только с правами администратора")
def удалить_подразделение(id: int, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return delete_department(id, session)