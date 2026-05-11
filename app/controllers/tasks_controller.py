from app.core.security import department_manager_required, get_current_user
from app.models.tasks import Tasks
from app.models.task_status import Task_Status
from app.models.task_comments import TaskComments
from app.models.departments_model import Departments
from app.models.employee_models import Employees
from app.schemas.task_schema import (
    TaskCreate,
    TasksGroupedByDepartment,
    DepartmentTasksGroup,
    TaskStatusUpdate,
    TaskCommentCreate,
    TaskCommentSchema,
    GetTaskSchema,
)
from datetime import datetime, timezone
from sqlmodel import Session, select
from typing import Optional, Dict, List, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page, Params, create_page

from app.models.users import Users


ALLOWED_PRIORITIES = {"малый", "средний", "высокий"}


def _as_stripped(value: Any) -> str:
    """Возвращает строковое значение без внешних пробелов.
    None и пустые значения приводятся к пустой строке.
    """
    return str(value or "").strip()


def _require_positive_int(value: Any, field_label: str) -> int:
    """Преобразует значение в положительное целое число.
    Вызывает HTTP 422, если значение невалидно.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Поле '{field_label}' должно быть целым числом"
        )
    if parsed <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Поле '{field_label}' должно быть больше нуля"
        )
    return parsed


def _validate_task_payload_required(payload: Dict[str, Any]) -> None:
    """Проверяет обязательные поля payload для создания задачи.
    Вызывает HTTP 422 при пустых или некорректных данных.
    """
    title = _as_stripped(payload.get("title"))
    description = _as_stripped(payload.get("description"))
    priority = _as_stripped(payload.get("priority")).lower()

    if not title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Поле 'title' обязательно"
        )
    if not description:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Поле 'description' обязательно"
        )
    if not priority:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Поле 'priority' обязательно"
        )
    if priority not in ALLOWED_PRIORITIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Поле 'priority' должно быть одним из: малый, средний, высокий"
        )

    _require_positive_int(payload.get("creator_id"), "creator_id")
    _require_positive_int(payload.get("assignee_id"), "assignee_id")
    _require_positive_int(payload.get("department_id"), "department_id")
    _require_positive_int(payload.get("status_id"), "status_id")

    planned_start_date = payload.get("planned_start_date")
    planned_end_date = payload.get("planned_end_date")
    if planned_start_date and planned_end_date and planned_end_date < planned_start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Поле 'planned_end_date' не может быть раньше 'planned_start_date'"
        )


def _resolve_creator_department_id(
    session: Session,
    creator_id: int,
    creator_emp: Optional[Employees],
    creator_user: Optional[Users]
) -> Optional[int]:
    """Определяет подразделение создателя задачи.
    Для администратора возвращает None как особый случай.
    """
    creator_is_admin = bool(creator_user and creator_user.role_id == 1)
    if creator_is_admin:
        return None

    if creator_user and creator_user.role_id == 2:
        managed_department = session.exec(
            select(Departments).where(Departments.department_manager_id == creator_id)
        ).first()
        if managed_department:
            return int(managed_department.id)

    if creator_emp:
        return int(creator_emp.department_id)
    return None


def _task_to_schema(task: Tasks, department_name: Optional[str] = None) -> GetTaskSchema:
    """Преобразование задачи в схему ответа."""
    comments = []
    for comment in getattr(task, "comments", []) or []:
        comments.append(
            TaskCommentSchema(
                id=comment.id,
                author_id=comment.author_id,
                author=comment.author.username if getattr(comment, "author", None) else "Неизвестно",
                comment_text=comment.comment_text,
                created_at=comment.created_at,
            )
        )
    comments.sort(key=lambda row: row.created_at)

    return GetTaskSchema(
        id=task.id,
        creator_id=task.creator_id,
        assignee_id=task.assignee_id,
        department_id=task.department_id,
        status_id=task.status_id,
        title=task.title,
        description=task.description,
        creator=task.creator.username if getattr(task, "creator", None) else "Неизвестно",
        assignee=task.assignee.username if getattr(task, "assignee", None) else "Неизвестно",
        department=(
            department_name
            or (task.department.name if getattr(task, "department", None) else "Неизвестно")
        ),
        status=task.status.name if getattr(task, "status", None) else "Неизвестно",
        priority=task.priority,
        planned_start_date=task.planned_start_date,
        planned_end_date=task.planned_end_date,
        actual_start_date=task.actual_start_date,
        actual_end_date=task.actual_end_date,
        comments=comments,
    )


def _ensure_task_access(task: Tasks, user: Users) -> None:
    """Проверяет, что пользователь имеет доступ к задаче.
    Доступ есть у создателя, исполнителя, админа и менеджера.
    """
    has_access = (
        task.creator_id == user.id
        or task.assignee_id == user.id
        or user.role_id == 1
        or user.role_id == 2
    )
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой задаче",
        )


def get_task_comments(task_id: int, session: Session, user: Users) -> List[TaskCommentSchema]:
    """Получение комментариев задачи по идентификатору."""
    try:
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Параметр 'task_id' должен быть больше нуля",
            )

        task = session.get(Tasks, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

        _ensure_task_access(task, user)

        comments_rows = session.exec(
            select(TaskComments).where(TaskComments.task_id == task_id).order_by(TaskComments.created_at)
        ).all()
        result = []
        for row in comments_rows:
            author = session.get(Users, row.author_id)
            result.append(
                TaskCommentSchema(
                    id=row.id,
                    author_id=row.author_id,
                    author=author.username if author else "Неизвестно",
                    comment_text=row.comment_text,
                    created_at=row.created_at,
                )
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )


def get_all_tasks(session: Session, user: Users = Depends(department_manager_required)) -> TasksGroupedByDepartment:
    """ Вывод информации, сгруппированной по подразделениям """
    try:
        sql = select(Tasks, Departments).join(Departments, Tasks.department_id == Departments.id).order_by(Departments.id, Tasks.id)
        results = session.exec(sql).all()
        grouped_tasks: Dict[int, Dict[str, Any]] = {}
        
        for task, department in results:
            if department.id not in grouped_tasks:
                grouped_tasks[department.id] = {
                    "department_id": department.id,
                    "department_name": department.name,
                    "tasks": []
                }
            grouped_tasks[department.id]["tasks"].append(_task_to_schema(task, department.name))
    
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

def get_tasks_by_department_id(session: Session, user: Users) -> Page[GetTaskSchema]:
    """ Вывод всех задач подразделения текущего пользователя """
    try:
        employee = session.exec(select(Employees).where(Employees.user_id == user.id)).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сотрудник не найден для данного пользователя"
            )
        sql = select(Tasks).where(Tasks.department_id == employee.department_id)
        tasks = session.exec(sql).all()
        tasks_schema = [_task_to_schema(task) for task in tasks]
        return create_page(tasks_schema, total=len(tasks_schema), params=Params())
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def get_my_tasks(session: Session, user: Users = Depends(get_current_user)) -> Page[GetTaskSchema]:
    """ Вывод всех задач текущего залогиненного пользователя (назначенные и созданные) """
    try:
        sql = select(Tasks).where(
            (Tasks.assignee_id == user.id) | (Tasks.creator_id == user.id)
        ).order_by(Tasks.department_id)
        tasks = session.exec(sql).all()
        tasks_schema = [_task_to_schema(task) for task in tasks]
        return create_page(tasks_schema, total=len(tasks_schema), params=Params())
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def post_task(data: TaskCreate, session: Session, user: Users = Depends(department_manager_required)) -> Optional[Tasks]:
    """ Добавление задачи (без необходимости указывать id) """
    try:
        payload = data.dict()
        _validate_task_payload_required(payload)
        assignee_emp = session.exec(select(Employees).where(Employees.user_id == payload["assignee_id"])).first()
        creator_emp = session.exec(select(Employees).where(Employees.user_id == payload["creator_id"])).first()
        creator_user = session.get(Users, payload["creator_id"])

        if not assignee_emp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Исполнитель должен быть привязан к подразделению"
            )
        assignee_department_id = int(assignee_emp.department_id)
        payload_department_id = int(payload["department_id"])
        creator_department_id = _resolve_creator_department_id(
            session=session,
            creator_id=int(payload["creator_id"]),
            creator_emp=creator_emp,
            creator_user=creator_user,
        )
        if creator_department_id is None and not (creator_user and creator_user.role_id == 1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Создатель должен быть привязан к подразделению"
            )

        if creator_department_id is not None and assignee_department_id != creator_department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Исполнитель и создатель должны быть из одного подразделения"
            )

        if payload_department_id != assignee_department_id:
            payload["department_id"] = assignee_department_id

        task = Tasks(**payload)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except HTTPException:
        raise
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
        if id <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Параметр 'id' должен быть больше нуля"
            )
        result= session.get(Tasks, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        session.delete(result)
        session.commit()
        return "Удаление выполнено"
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Внутренняя ошибка сервера: {str(e)}")

def put_task(id: int, data: Tasks, session: Session, user: Users = Depends(get_current_user)) -> Tasks:
    """ Изменение """
    try:
        if id <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Параметр 'id' должен быть больше нуля"
            )
        result= session.get(Tasks, id)
        if not result :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"идентификатор не найден")
        updates = data.dict(exclude_unset=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Не переданы поля для обновления задачи"
            )
        is_admin = user.role_id == 1
        is_manager = user.role_id == 2
        if not (is_admin or is_manager):
            has_access = result.creator_id == user.id or result.assignee_id == user.id
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="У вас нет доступа к редактированию этой задачи",
                )
            allowed_fields_for_employee = {"status_id", "actual_start_date", "actual_end_date"}
            forbidden_fields = sorted(set(updates.keys()) - allowed_fields_for_employee)
            if forbidden_fields:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Сотрудник может изменять только статус и фактические даты "
                        "(actual_start_date, actual_end_date)"
                    ),
                )

        if "title" in updates and not _as_stripped(updates.get("title")):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Поле 'title' не может быть пустым"
            )
        if "description" in updates and not _as_stripped(updates.get("description")):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Поле 'description' не может быть пустым"
            )
        if "priority" in updates:
            priority = _as_stripped(updates.get("priority")).lower()
            if not priority:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Поле 'priority' не может быть пустым"
                )
            if priority not in ALLOWED_PRIORITIES:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Поле 'priority' должно быть одним из: малый, средний, высокий"
                )
            updates["priority"] = priority

        for numeric_field in ("assignee_id", "creator_id", "department_id", "status_id"):
            if numeric_field in updates:
                updates[numeric_field] = _require_positive_int(updates.get(numeric_field), numeric_field)
        if "planned_start_date" in updates or "planned_end_date" in updates:
            start_date = updates.get("planned_start_date", result.planned_start_date)
            end_date = updates.get("planned_end_date", result.planned_end_date)
            if start_date and end_date and end_date < start_date:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Поле 'planned_end_date' не может быть раньше 'planned_start_date'"
                )

        assignee_id = updates.get("assignee_id", result.assignee_id)
        creator_id = updates.get("creator_id", result.creator_id)
        department_id = updates.get("department_id", result.department_id)

        assignee_emp = session.exec(select(Employees).where(Employees.user_id == assignee_id)).first()
        creator_emp = session.exec(select(Employees).where(Employees.user_id == creator_id)).first()
        creator_user = session.get(Users, creator_id)
        creator_department_id = _resolve_creator_department_id(
            session=session,
            creator_id=int(creator_id),
            creator_emp=creator_emp,
            creator_user=creator_user,
        )

        if not assignee_emp or (creator_department_id is None and not (creator_user and creator_user.role_id == 1)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Создатель и исполнитель должны быть привязаны к подразделению"
            )
        if int(assignee_emp.department_id) != int(department_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Задачу можно ставить только в подразделении исполнителя"
            )
        if creator_department_id is not None and int(creator_department_id) != int(department_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Задачу можно ставить только в подразделении исполнителя и создателя"
            )

        for key, value in updates.items():
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

def update_task_status(task_id: int, status_data: TaskStatusUpdate, session: Session, user: Users) -> Tasks:
    """ Изменение статуса задачи пользователем, имеющим доступ к задаче """
    try:
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Параметр 'task_id' должен быть больше нуля"
            )
        status_name = _as_stripped(status_data.status_name)
        if not status_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Поле 'status_name' обязательно"
            )

        task = session.get(Tasks, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

        has_access = (
            task.creator_id == user.id or 
            task.assignee_id == user.id or
            user.role_id == 1 or
            user.role_id == 2
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет доступа к изменению статуса этой задачи"
            )
        
        status_obj = session.exec(select(Task_Status).where(Task_Status.name == status_name)).first()
        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Статус '{status_name}' не найден"
            )
        
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
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Параметр 'task_id' должен быть больше нуля"
            )
        comment_text = _as_stripped(comment_data.comment_text)
        if not comment_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Поле 'comment_text' обязательно"
            )

        task = session.get(Tasks, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        
        has_access = (
            task.creator_id == user.id or 
            task.assignee_id == user.id or
            user.role_id == 1 or
            user.role_id == 2
        )
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет доступа к добавлению комментария к этой задаче"
            )
        
        comment = TaskComments(
            task_id=task_id,
            author_id=user.id,
            comment_text=comment_text
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
