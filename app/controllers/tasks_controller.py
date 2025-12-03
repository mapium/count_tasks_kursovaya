from app.core.security import department_manager_required, get_current_user
from app.models.tasks import Tasks
from app.models.task_status import Task_Status
from app.models.task_comments import TaskComments
from app.models.departments_model import Departments
from app.models.employee_models import Employees
from app.schemas.task_schema import TaskCreate, TasksGroupedByDepartment, DepartmentTasksGroup, TaskStatusUpdate, TaskCommentCreate
from datetime import datetime, timezone
from sqlmodel import Session, select
from typing import Optional, Dict, List, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from app.models.users import Users

def get_all_tasks(session: Session, user: Users = Depends(department_manager_required)) -> TasksGroupedByDepartment:
    """ Вывод информации, сгруппированной по подразделениям """
    try:
        # Получаем все задачи с информацией об отделах через JOIN
        sql = select(Tasks, Departments).join(Departments, Tasks.department_id == Departments.id).order_by(Departments.id, Tasks.id)
        results = session.exec(sql).all()
        
        # Группируем задачи по отделам
        grouped_tasks: Dict[int, Dict[str, Any]] = {}
        
        for task, department in results:
            if department.id not in grouped_tasks:
                grouped_tasks[department.id] = {
                    "department_id": department.id,
                    "department_name": department.name,
                    "tasks": []
                }
            grouped_tasks[department.id]["tasks"].append(task)
        
        # Преобразуем в список групп
        departments_groups = [
            DepartmentTasksGroup(
                department_id=group["department_id"],
                department_name=group["department_name"],
                tasks=group["tasks"]
            )
            for group in grouped_tasks.values()
        ]
        
        return TasksGroupedByDepartment(departments=departments_groups)
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Внутренняя ошибка сервера: {str(e)}")

def get_tasks_by_department_id(session: Session, user: Users) -> Page[Tasks]:
    """ Вывод всех задач подразделения текущего пользователя """
    try:
        # Находим сотрудника по user_id, чтобы получить department_id
        employee = session.exec(select(Employees).where(Employees.user_id == user.id)).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сотрудник не найден для данного пользователя"
            )
        
        # Получаем задачи только подразделения пользователя
        sql = select(Tasks).where(Tasks.department_id == employee.department_id)
        return paginate(session, sql)
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def get_my_tasks(session: Session, user: Users = Depends(get_current_user)) -> Page[Tasks]:
    """ Вывод всех задач текущего залогиненного пользователя (назначенные и созданные) """
    try:
        sql = select(Tasks).where(
            (Tasks.assignee_id == user.id) | (Tasks.creator_id == user.id)
        ).order_by(Tasks.department_id)
        return paginate(session, sql)
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def post_task(data: TaskCreate, session: Session, user: Users = Depends(department_manager_required)) -> Optional[Tasks]:
    """ Добавление задачи (без необходимости указывать id) """
    try:
        task = Tasks(**data.dict())
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Ошибка: дубликат или нарушение целостности данных")
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def delete_task(id: int, session: Session, user: Users = Depends(department_manager_required)) -> str:
    """ Удаление """
    try:
        result= session.get(Tasks, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        session.delete(result)
        session.commit()
        return "Удаление выполнено"
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def put_task(id: int, data: Tasks, session: Session, user: Users = Depends(department_manager_required)) -> Tasks:
    """ Изменение """
    try:
        result= session.get(Tasks, id)
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

def update_task_status(task_id: int, status_data: TaskStatusUpdate, session: Session, user: Users) -> Tasks:
    """ Изменение статуса задачи пользователем, имеющим доступ к задаче """
    try:
        task = session.get(Tasks, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        
        # Проверка доступа: пользователь должен быть создателем или исполнителем задачи
        # Администраторы и руководители отделов имеют доступ ко всем задачам
        has_access = (
            task.creator_id == user.id or 
            task.assignee_id == user.id or
            user.role_id == 1 or  # Администратор
            user.role_id == 2     # Руководитель отдела
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет доступа к изменению статуса этой задачи"
            )
        
        # Ищем статус по названию
        status_obj = session.exec(select(Task_Status).where(Task_Status.name == status_data.status_name)).first()
        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статус '{status_data.status_name}' не найден"
            )
        
        # Обновляем статус
        task.status_id = status_obj.id
        task.updated_at = datetime.now(timezone.utc)
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def add_comment_to_task(task_id: int, comment_data: TaskCommentCreate, session: Session, user: Users) -> TaskComments:
    """ Добавление комментария к задаче """
    try:
        # Проверяем, что задача существует
        task = session.get(Tasks, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        
        # Проверка доступа: пользователь должен иметь доступ к задаче
        # Администраторы и руководители отделов имеют доступ ко всем задачам
        has_access = (
            task.creator_id == user.id or 
            task.assignee_id == user.id or
            user.role_id == 1 or  # Администратор
            user.role_id == 2     # Руководитель отдела
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет доступа к добавлению комментария к этой задаче"
            )
        
        # Создаем комментарий
        comment = TaskComments(
            task_id=task_id,
            author_id=user.id,
            comment_text=comment_data.comment_text
        )
        
        session.add(comment)
        session.commit()
        session.refresh(comment)
        
        return comment
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")
