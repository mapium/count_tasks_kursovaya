from app.models.employee_models import Employees
from sqlmodel import Session, select
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate


def get_all_employees(session: Session) -> Page[Employees]:
    """ Вывод информации """
    try:
        sql = select(Employees)
        return paginate(session, sql)
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Внутренняя ошибка сервера: {str(e)}")

def get_employee_by_id(id: int, session: Session) -> Employees:
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

def post_employee(data: Employees, session: Session) -> Optional[Employees]:
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

def delete_employee(id: int, session: Session) -> str:
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

def put_employee(id: int, data: Employees, session: Session) -> Employees:
    """ Изменение """
    try:
        result= session.get(Employees, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        for key, value in data.dict(exclude_unset=True).items():
            setattr(result, key, value)
        session.add(result)
        session.commit()
        session.refresh(result)
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")
