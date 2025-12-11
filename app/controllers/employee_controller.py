from app.models.employee_models import Employees
from app.models.users import Users
from app.models.departments_model import Departments
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
        
        # Обработка user_id: проверка существования и занятости
        if 'user_id' in update_data and update_data['user_id'] is not None:
            user_id = update_data['user_id']
            
            # Проверяем, существует ли пользователь
            existing_user = session.get(Users, user_id)
            
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Пользователь с ID {user_id} не найден"
                )
            
            # Проверяем, не занят ли пользователь другим сотрудником
            other_employee = session.exec(
                select(Employees).where(
                    Employees.user_id == user_id,
                    Employees.id != id
                )
            ).first()
            
            if other_employee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Пользователь с ID {user_id} уже привязан к другому сотруднику"
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

def get_my_department_employees(session: Session, user: Users) -> Page[Employees]:
    """ Вывод всех работников подразделения менеджера """
    try:
        # Находим подразделение, где текущий пользователь является менеджером
        department = session.exec(
            select(Departments).where(Departments.department_manager_id == user.id)
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подразделение не найдено для данного менеджера"
            )
        
        # Получаем всех сотрудников этого подразделения
        sql = select(Employees).where(Employees.department_id == department.id)
        return paginate(session, sql)
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

def post_employee_to_my_department(data: EmployeeCreate, session: Session, user: Users) -> Optional[Employees]:
    """ Добавление работника только в свой отдел менеджера """
    try:
        # Находим подразделение, где текущий пользователь является менеджером
        department = session.exec(
            select(Departments).where(Departments.department_manager_id == user.id)
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подразделение не найдено для данного менеджера"
            )
        
        # Проверяем, что сотрудник добавляется в подразделение менеджера
        if data.department_id != department.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Вы можете добавлять работников только в свой отдел (ID: {department.id})"
            )
        
        # Создаем сотрудника
        employee = Employees(**data.dict(exclude_unset=True))
        session.add(employee)
        session.commit()
        session.refresh(employee)
        return employee
    except HTTPException:
        raise
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка: дубликат или нарушение целостности данных"
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

def delete_employee_from_my_department(id: int, session: Session, user: Users) -> str:
    """ Удаление работника только из своего отдела менеджера """
    try:
        # Находим подразделение, где текущий пользователь является менеджером
        department = session.exec(
            select(Departments).where(Departments.department_manager_id == user.id)
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подразделение не найдено для данного менеджера"
            )
        
        # Находим работника
        employee = session.get(Employees, id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Работник не найден"
            )
        
        # Проверяем, что работник принадлежит подразделению менеджера
        if employee.department_id != department.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете удалять работников только из своего отдела"
            )
        
        session.delete(employee)
        session.commit()
        return "Удаление выполнено"
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

def put_employee_from_my_department(id: int, data: EmployeeUpdate, session: Session, user: Users) -> Employees:
    """ Изменение работника только из своего отдела менеджера """
    try:
        # Находим подразделение, где текущий пользователь является менеджером
        department = session.exec(
            select(Departments).where(Departments.department_manager_id == user.id)
        ).first()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подразделение не найдено для данного менеджера"
            )
        
        # Находим работника
        employee = session.get(Employees, id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Работник не найден"
            )
        
        # Проверяем, что работник принадлежит подразделению менеджера
        if employee.department_id != department.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете изменять работников только из своего отдела"
            )
        
        update_data = data.dict(exclude_unset=True)
        
        # Проверка: менеджер не может переводить работника в другой отдел
        if 'department_id' in update_data:
            if update_data['department_id'] != department.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Вы можете изменять работников только в рамках своего отдела"
                )
        
        # Обработка user_id: проверка существования и занятости
        if 'user_id' in update_data and update_data['user_id'] is not None:
            user_id = update_data['user_id']
            
            # Проверяем, существует ли пользователь
            existing_user = session.get(Users, user_id)
            
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Пользователь с ID {user_id} не найден"
                )
            
            # Проверяем, не занят ли пользователь другим сотрудником
            other_employee = session.exec(
                select(Employees).where(
                    Employees.user_id == user_id,
                    Employees.id != id
                )
            ).first()
            
            if other_employee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Пользователь с ID {user_id} уже привязан к другому сотруднику"
                )
        
        # Обновляем данные
        for key, value in update_data.items():
            setattr(employee, key, value)
        session.add(employee)
        session.commit()
        session.refresh(employee)
        return employee
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )
