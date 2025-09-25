import psycopg2
from models.employee_models import Employees
from models.users_model import Users 
from psycopg2.extras import RealDictCursor
from db.database import engine
from sqlmodel import Session, select


def add_employee(first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id):
    """
    Добавление нового сотрудника
    """
    with Session(engine) as session:
        employee = Employees(first_name=first_name, last_name=last_name, middle_name=middle_name, phone_number=phone_number, email=email, passport_data=passport_data, inn=inn, snils=snils, department_id=department_id)
        session.add(employee)
        session.commit()
        return True

def get_all_employees():
    """
    Получение всех сотрудников
    """
    with Session(engine) as session:
        employees = session.exec(select(Employees)).all()
        return employees


def edit_department_id(employee_id, new_department_id):
    """
    Редактирование department_id у сотрудника
    """
    with Session(engine) as session:
        employee_id_int = int(str(employee_id).strip())
        new_department_id_int = int(str(new_department_id).strip())
        employee = session.get(Employees, employee_id_int)
        if employee is None:
            return False
        employee.department_id = new_department_id_int
        session.commit()
        return True

def del_employee(employee_id):
    """
    Удаление сотрудника
    """
    with Session(engine) as session:
        employee = session.get(Employees, employee_id)
        if employee:
            session.delete(employee)
            session.commit()
            return True
        else:
            return False