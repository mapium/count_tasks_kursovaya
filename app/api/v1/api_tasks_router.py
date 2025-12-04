from fastapi import APIRouter, Depends
from sqlmodel import Session
from fastapi_pagination import Page
from app.core.security import department_manager_required, get_current_user
from app.db.session import get_session
from app.controllers.tasks_controller import get_all_tasks, get_tasks_by_department_id, get_my_tasks, post_task, delete_task, put_task, update_task_status, add_comment_to_task
from app.models.tasks import Tasks
from app.models.task_comments import TaskComments
from app.models.users import Users
from app.schemas.task_schema import TaskCreate, TasksGroupedByDepartment, TaskStatusUpdate, TaskCommentCreate

router = APIRouter() 

@router.get("/tasks", tags=["Задачи"], response_model=TasksGroupedByDepartment, description="Вывод информации, сгруппированной по подразделениям")
def Показать_все_задачи_подразделений(session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return get_all_tasks(session, user)

@router.get("/tasks/my-department", tags=["Задачи"], response_model=Page[Tasks], description="Вывод всех задач подразделения текущего пользователя")
def Вывод_задач_своего_подразделения(session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    return get_tasks_by_department_id(session, user)

@router.get("/tasks/my", tags=["Задачи"], response_model=Page[Tasks], description="Вывод всех задач текущего залогиненного пользователя")
def Показать_мои_задачи(session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    return get_my_tasks(session, user)

@router.post("/tasks", tags=["Задачи"], response_model=Tasks, description="только с правами менеджера и выше")
def добавить_задачу(task: TaskCreate, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return post_task(task, session)

@router.put("/tasks/{id}", tags=["Задачи"], description="только с правами менеджера и выше")
def изменить_задачу(id: int, data: Tasks, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return put_task(id, data, session)

@router.delete("/tasks/{id}", tags=["Задачи"], description="только с правами менеджера и выше")
def удалить_задачу(id: int, session: Session = Depends(get_session), user: Users = Depends(department_manager_required)):
    return delete_task(id, session)

@router.patch("/tasks/{task_id}/status", tags=["Задачи"], response_model=Tasks, description="""Изменение статуса задачи (доступно создателю, исполнителю, администратору или руководителю отдела)
Названия статусов: "К выполнению"
"В работе"
"На проверке"
"Выполнено" """)
def изменить_статус_задачи(task_id: int, status_data: TaskStatusUpdate, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    return update_task_status(task_id, status_data, session, user)

@router.post("/tasks/{task_id}/comments", tags=["Задачи"], response_model=TaskComments, description="Добавление комментария к задаче (доступно создателю, исполнителю, администратору или руководителю отдела)")
def добавить_комментарий_к_задаче(task_id: int, comment_data: TaskCommentCreate, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    return add_comment_to_task(task_id, comment_data, session, user)