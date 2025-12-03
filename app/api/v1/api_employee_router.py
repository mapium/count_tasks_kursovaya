from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.security import admin_required, get_current_user
from app.db.session import get_session
from app.controllers.employee_controller import get_all_employees, get_employee_by_id, post_employee, delete_employee, put_employee
from app.models import Users
from app.models.employee_models import Employees
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from fastapi_pagination import Page

router = APIRouter() 

@router.get("/employees", tags=["employees"], response_model=Page[Employees], description="Только с правами администратора")
def список_сотрудников(session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return get_all_employees(session)

@router.get("/employees/{id}", tags=["employees"])
def сотрудник_по_id(id: int, session: Session = Depends(get_session), user: Users = Depends(admin_required), description="Только с правами администратора"):
    return get_employee_by_id(id, session)

@router.post("/employees", tags=["employees"], response_model=Employees, 
             description="Создание нового сотрудника. Только с правами администратора Валидация: паспорт - минимум 10 символов, ИНН - минимум 12 символов, СНИЛС - минимум 11 символов.")
def добавление_сотрудника(employee: EmployeeCreate, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return post_employee(employee, session)

@router.put("/employees/{id}", tags=["employees"], response_model=Employees,
            description="Обновление данных сотрудника. Валидация: паспорт - минимум 10 символов, ИНН - минимум 12 символов, СНИЛС - минимум 11 символов. Доступ: администратор, менеджер отдела или сам сотрудник (только свои данные).")
def изменение_сотрудника(id: int, data: EmployeeUpdate, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    return put_employee(id, data, session, user)

@router.delete("/employees/{id}", tags=["employees"], description="Только с правами администратора")
def увольнение_сотрудника(id: int, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return delete_employee(id, session)