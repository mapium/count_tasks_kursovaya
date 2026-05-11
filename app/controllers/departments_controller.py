from app.models.departments_model import Departments
from app.models.users import Users
from sqlmodel import Session, select
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from app.schemas.departments_schema import DepartmentsCreateSchema


def _validate_department_manager(session: Session, manager_id: Optional[int]):
    """Проверяет корректность менеджера для привязки к подразделению.
    Разрешает только роль менеджера и единственную привязку.
    """
    if manager_id is None:
        return
    manager = session.get(Users, manager_id)
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Менеджер не найден",
        )
    if manager.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Привязать можно только пользователя с ролью менеджера",
        )
    existing_department = session.exec(
        select(Departments).where(Departments.department_manager_id == manager_id)
    ).first()
    if existing_department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Менеджер уже привязан к другому подразделению",
        )

def get_all_departments(session: Session) -> Page[Departments]:
    """ Вывод информации """
    try:
        sql = select(Departments)
        return paginate(session, sql)
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Внутренняя ошибка сервера: {str(e)}")

def get_department_by_id(id: int, session: Session) -> Departments:
    """ Поиск по идентификатору """
    try:
        result = session.get(Departments, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def post_department(data: DepartmentsCreateSchema, session: Session) -> Optional[Departments]:
    """ Добавление """
    try:
        _validate_department_manager(session, data.department_manager_id)
        obj = Departments(**data.dict())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Ошибка: дубликат или нарушение целостности данных")
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def delete_department(id: int, session: Session) -> str:
    """ Удаление """
    try:
        result= session.get(Departments, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        session.delete(result)
        session.commit()
        return "Удаление выполнено"
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def put_department(id: int, data: DepartmentsCreateSchema, session: Session) -> Departments:
    """ Изменение """
    try:
        result= session.get(Departments, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        updates = data.dict(exclude_unset=True)
        next_manager_id = updates.get("department_manager_id")
        if next_manager_id is not None and next_manager_id != result.department_manager_id:
            _validate_department_manager(session, next_manager_id)
        for key, value in updates.items():
            setattr(result, key, value)
        session.add(result)
        session.commit()
        session.refresh(result)
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")
