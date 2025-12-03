from app.models.employee_models import Employees
from app.models.users import Users
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
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

def post_employee(data: EmployeeCreate, session: Session) -> Optional[Employees]:
    """ Добавление сотрудника с валидацией данных """
    try:
        employee = Employees(**data.dict(exclude_unset=True))
        session.add(employee)
        session.commit()
        session.refresh(employee)
        return employee
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

def put_employee(id: int, data: EmployeeUpdate, session: Session, user: Users) -> Employees:
    """ Изменение сотрудника с валидацией данных """
    try:
        result = session.get(Employees, id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        
        # Проверка прав доступа
        is_admin = user.role_id == 1
        is_manager = user.role_id == 2
        is_self = result.user_id == user.id
        
        # Если пользователь не админ, не менеджер и не сам сотрудник - запретить доступ
        if not (is_admin or is_manager or is_self):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете обновлять только свои данные"
            )
        
        update_data = data.dict(exclude_unset=True)
        
        # Проверка: только администратор может изменять is_active
        if 'is_active' in update_data and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администратор может изменять поле is_active"
            )
        
        # Если пользователь - сам сотрудник (не админ и не менеджер), ограничить поля
        if is_self and not (is_admin or is_manager):
            # Сотрудник не может менять критичные поля
            restricted_fields = {'user_id', 'department_id'}
            
            # Проверяем, не пытается ли сотрудник изменить запрещенные поля
            for field in restricted_fields:
                if field in update_data:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Вы не можете изменять поле {field}"
                    )
        
        # Обновляем данные
        for key, value in update_data.items():
            setattr(result, key, value)
        session.add(result)
        session.commit()
        session.refresh(result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")
