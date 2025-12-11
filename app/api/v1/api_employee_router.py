from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.security import admin_required, get_current_user, department_manager_required
from app.db.session import get_session
from app.controllers.employee_controller import (
    get_all_employees, 
    get_employee_by_id, 
    post_employee, 
    delete_employee, 
    put_employee, 
    get_my_department_employees, 
    post_employee_to_my_department,
    delete_employee_from_my_department,
    put_employee_from_my_department
)
from app.models import Users
from app.models.employee_models import Employees
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from fastapi_pagination import Page

router = APIRouter() 



@router.post("/employees/manager-department", tags=["Сотрудники"], response_model=Employees,
             description="Добавление работника только в отдел менеджера. Только для менеджеров. Валидация: паспорт -  10 символов, ИНН -  12 символов, СНИЛС -  11 символов.")
def добавление_работника_в_отдел_менеджера(employee: EmployeeCreate, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return post_employee_to_my_department(employee, session, user)

@router.put("/employees/manager-department/{id}", tags=["Сотрудники"], response_model=Employees,
            description="Изменение работника только из своего отдела. Только для менеджеров. Валидация: паспорт -  10 символов, ИНН -  12 символов, СНИЛС -  11 символов.")
def изменение_работника_из_своего_отдела(id: int, data: EmployeeUpdate, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return put_employee_from_my_department(id, data, session, user)

@router.delete("/employees/manager-department/{id}", tags=["Сотрудники"], 
               description="Удаление работника только из своего отдела. Только для менеджеров.")
def удаление_работника_из_своего_отдела(id: int, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return delete_employee_from_my_department(id, session, user)
@router.get("/employees", tags=["Сотрудники"], response_model=Page[Employees], description="Только с правами администратора")
def список_сотрудников(session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return get_all_employees(session)

@router.get("/employees/manager-department", tags=["Сотрудники"], response_model=Page[Employees], description="Вывод всех работников подразделения менеджера. Только для менеджеров.")
def список_работников_подразделения_по_менеджеру(session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return get_my_department_employees(session, user)
@router.get("/employees/{id}", tags=["Сотрудники"], description="Только с правами администратора")
def сотрудник_по_id(id: int, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return get_employee_by_id(id, session)

@router.post("/employees", tags=["Сотрудники"], response_model=Employees, 
             description="Создание нового сотрудника. Только с правами администратора Валидация: паспорт -  10 символов, ИНН -  12 символов, СНИЛС -  11 символов.")
def добавление_сотрудника(employee: EmployeeCreate, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return post_employee(employee, session)

@router.put("/employees/{id}", tags=["Сотрудники"], response_model=Employees, description="Обновление данных сотрудника. Валидация: паспорт -  10 символов, ИНН -  12 символов, СНИЛС -  11 символов. Доступ: администратор, менеджер отдела или сам сотрудник (только свои данные).")
def изменение_сотрудника(id: int, data: EmployeeUpdate, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    return put_employee(id, data, session, user)

@router.delete("/employees/{id}", tags=["Сотрудники"], description="Только с правами администратора")
def увольнение_сотрудника(id: int, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return delete_employee(id, session)