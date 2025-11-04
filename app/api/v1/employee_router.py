from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.controllers.employee_controller import get_all_employees, get_employee_by_id, post_employee, delete_employee
from app.models.employee_models import Employees
router = APIRouter() 
@router.get("/employees")
def show_employees_route(session: Session = Depends(get_session)):
    return get_all_employees(session)
@router.get("/employees/{id}")
def show_employee_by_id_route(id: int, session: Session = Depends(get_session)):
    return get_employee_by_id(id, session)
@router.post("/employees")
def add_employee_route(employee: Employees, session: Session = Depends(get_session)):
    return post_employee(employee, session)
@router.delete("/employees/{id}")
def delete_employee_route(id: int, session: Session = Depends(get_session)):
    return delete_employee(id, session)