from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.controllers.tasks_controller import get_all_tasks, get_task_by_id, post_task, delete_task, put_task
from app.models.tasks import Tasks

router = APIRouter() 

@router.get("/tasks", tags=["tasks"])
def show_tasks_route(session: Session = Depends(get_session)):
    return get_all_tasks(session)

@router.get("/tasks/{id}", tags=["tasks"])
def show_task_by_id_route(id: int, session: Session = Depends(get_session)):
    return get_task_by_id(id, session)

@router.post("/tasks", tags=["tasks"])
def add_task_route(task: Tasks, session: Session = Depends(get_session)):
    return post_task(task, session)

@router.put("/tasks/{id}", tags=["tasks"])
def put_task_route(id: int, data: Tasks, session: Session = Depends(get_session)):
    return put_task(id, data, session)

@router.delete("/tasks/{id}", tags=["tasks"])
def delete_task_route(id: int, session: Session = Depends(get_session)):
    return delete_task(id, session)