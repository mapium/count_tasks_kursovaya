from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.controllers.departments_controller import get_all_departments, get_department_by_id, post_department, delete_department, put_department
from app.models.departments_model import Departments

router = APIRouter() 

@router.get("/departments", tags=["departments"])
def show_departments_route(session: Session = Depends(get_session)):
    return get_all_departments(session)

@router.get("/departments/{id}", tags=["departments"])
def show_employee_by_id_route(id: int, session: Session = Depends(get_session)):
    return get_department_by_id(id, session)

@router.post("/departments", tags=["departments"])
def add_employee_route(employee: Departments, session: Session = Depends(get_session)):
    return post_department(employee, session)

@router.put("/departments/{id}", tags=["departments"])
def put_employee_route(id: int, data: Departments, session: Session = Depends(get_session)):
    return put_department(id, data, session)

@router.delete("/departments/{id}", tags=["departments"])
def delete_employee_route(id: int, session: Session = Depends(get_session)):
    return delete_department(id, session)