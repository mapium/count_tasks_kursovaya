from app.models.employee_models import Employees
from sqlmodel import Session, select
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from app.db.session import get_session
from sqlalchemy.exc import IntegrityError

def get_all_employees(session: Session = Depends(get_session)) -> List[Employees]:
    """ Вывод информации """
    try:
        sql=select(Employees)
        result=session.exec(sql).all()
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Внутренняя ошибка сервера: {str(e)}")

def get_employee_by_id(id: int, session: Session = Depends(get_session)) -> Employees:
    """ Поиск по идентификатору """
    try:
        result = session.get(Employees, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def post_employee(data: Employees, session: Session = Depends(get_session)) -> Optional[Employees]:
    """ Добавление """
    try:
        session.add(data)
        session.commit()
        session.refresh(data)
        return data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Ошибка: дубликат или нарушение целостности данных")
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def delete_employee(id: int, session: Session = Depends(get_session)) -> str:
    """ Удаление """
    try:
        result= session.get(Employees, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        session.delete(result)
        session.commit()
        return "Удаление выполнено"
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

# def add_employee(first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id):
#     """
#     Добавление нового сотрудника
#     """
#     with Session(engine) as session:
#         employee = Employees(first_name=first_name, last_name=last_name, middle_name=middle_name, phone_number=phone_number, email=email, passport_data=passport_data, inn=inn, snils=snils, department_id=department_id)
#         session.add(employee)
#         session.commit()
#         return True

# def get_all_employees():
#     """
#     Получение всех сотрудников
#     """
#     with Session(engine) as session:
#         employees = session.exec(select(Employees)).all()
#         return employees


# def edit_department_id(employee_id, new_department_id):
#     """
#     Редактирование department_id у сотрудника
#     """
#     with Session(engine) as session:
#         employee_id_int = int(str(employee_id).strip())
#         new_department_id_int = int(str(new_department_id).strip())
#         employee = session.get(Employees, employee_id_int)
#         if employee is None:
#             return False
#         employee.department_id = new_department_id_int
#         session.commit()
#         return True

# def del_employee(employee_id):
#     """
#     Удаление сотрудника
#     """
#     with Session(engine) as session:
#         employee = session.get(Employees, employee_id)
#         if employee:
#             session.delete(employee)
#             session.commit()
#             return True
#         else:
#             return False