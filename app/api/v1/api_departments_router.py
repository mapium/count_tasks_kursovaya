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

@router.get("/departments", tags=["Подразделения"], response_model=Page[Departments],summary="Список подразделений")
def departments_list_route(session: Session = Depends(get_session)):
    return get_all_departments(session)

@router.get("/departments/{id}", tags=["Подразделения"], summary="Подразделение по идентификатору")
def department_by_id_route(id: int, session: Session = Depends(get_session)):
    return get_department_by_id(id, session)

@router.post("/departments", tags=["Подразделения"], description="Только с правами администратора", summary="Создание подразделения")
def create_department_route(employee: DepartmentsCreateSchema, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return post_department(employee, session)

@router.put("/departments/{id}", tags=["Подразделения"], description="Только с правами администратора", summary="Изменить подразделение")
def put_department_route(id: int, data: DepartmentsCreateSchema, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return put_department(id, data, session)

@router.delete("/departments/{id}", tags=["Подразделения"], description="Только с правами администратора", summary="Удалить подразделение")
def delete_department_route(id: int, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return delete_department(id, session)