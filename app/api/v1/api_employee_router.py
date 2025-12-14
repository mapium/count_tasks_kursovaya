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
             description="Добавление работника только в отдел менеджера. Только для менеджеров. Валидация: паспорт -  10 символов, ИНН -  12 символов, СНИЛС -  11 символов.", summary="Добавление работника в отдел менеджера")
def post_employee_to_my_department_route(employee: EmployeeCreate, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return post_employee_to_my_department(employee, session, user)

@router.put("/employees/manager-department/{id}", tags=["Сотрудники"], response_model=Employees,
            description="Изменение работника только из своего отдела. Только для менеджеров. Валидация: паспорт -  10 символов, ИНН -  12 символов, СНИЛС -  11 символов.", summary="Изменение работника из своего отдела")
def put_employee_from_my_department_route(id: int, data: EmployeeUpdate, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return put_employee_from_my_department(id, data, session, user)

@router.delete("/employees/manager-department/{id}", tags=["Сотрудники"], 
               description="Удаление работника только из своего отдела. Только для менеджеров.", summary="Удаление работника из своего отдела")
def delete_employee_from_my_department_route(id: int, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return delete_employee_from_my_department(id, session, user)
@router.get("/employees", tags=["Сотрудники"], response_model=Page[Employees], description="Только с правами администратора", summary="Список сотрудников")
def employees_list_route(session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return get_all_employees(session)

@router.get("/employees/manager-department", tags=["Сотрудники"], response_model=Page[Employees], description="Вывод всех работников подразделения менеджера. Только для менеджеров.", summary="Список работников подразделения по менеджеру")
def my_department_employees_route(session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return get_my_department_employees(session, user)
@router.get("/employees/{id}", tags=["Сотрудники"], description="Только с правами администратора", summary="Сотрудник по id")
def employee_by_id_route(id: int, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return get_employee_by_id(id, session)

@router.post("/employees", tags=["Сотрудники"], response_model=Employees, 
             description="Создание нового сотрудника. Только с правами администратора Валидация: паспорт -  10 символов, ИНН -  12 символов, СНИЛС -  11 символов.", summary="Добавление сотрудника")
def create_employee_route(employee: EmployeeCreate, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return post_employee(employee, session)

@router.put("/employees/{id}", tags=["Сотрудники"], response_model=Employees, description="Обновление данных сотрудника. Валидация: паспорт -  10 символов, ИНН -  12 символов, СНИЛС -  11 символов. Доступ: администратор, менеджер отдела или сам сотрудник (только свои данные).", summary="Изменение сотрудника")
def put_employee_route(id: int, data: EmployeeUpdate, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    return put_employee(id, data, session, user)

@router.delete("/employees/{id}", tags=["Сотрудники"], description="Только с правами администратора", summary="Увольнение сотрудника")
def delete_employee_route(id: int, session: Session = Depends(get_session), user: Users = Depends(admin_required)):
    return delete_employee(id, session)