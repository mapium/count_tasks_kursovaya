from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.controllers.employee_controller import get_all_employees, get_employee_by_id, post_employee, delete_employee, put_employee
from app.models.employee_models import Employees
from fastapi_pagination import Page

router = APIRouter() 

@router.get("/employees", tags=["employees"], response_model=Page[Employees])
def show_employees_route(session: Session = Depends(get_session)):
    return get_all_employees(session)

@router.get("/employees/{id}", tags=["employees"])
def show_employee_by_id_route(id: int, session: Session = Depends(get_session)):
    return get_employee_by_id(id, session)

@router.post("/employees", tags=["employees"])
def add_employee_route(employee: Employees, session: Session = Depends(get_session)):
    return post_employee(employee, session)

@router.put("/employees/{id}", tags=["employees"])
def put_employee_route(id: int, data: Employees, session: Session = Depends(get_session)):
    return put_employee(id, data, session)

@router.delete("/employees/{id}", tags=["employees"])
def delete_employee_route(id: int, session: Session = Depends(get_session)):
    return delete_employee(id, session)