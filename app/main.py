from app.db.database import init_db, close_db
from app.api.v1.api_employee_router import router as employee_router
from app.api.v1.api_departments_router import router as departments_router
from app.api.v1.api_tasks_router import router as tasks_router
from app.controllers.employee_controller import *
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi_pagination import add_pagination
from starlette.staticfiles import StaticFiles
from app.api.v1.api_users_router import router as user_router
from app.core.security import oauth2_scheme
@asynccontextmanager
async def on_startup(app: FastAPI):
    init_db()
    yield
    close_db()

app_v1 = FastAPI(title="AccountsAPI", lifespan=on_startup)
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
app_v1.include_router(user_router, prefix="/api/v1")
app_v1.include_router(employee_router, prefix="/api/v1")
app_v1.include_router(departments_router, prefix="/api/v1")
app_v1.include_router(tasks_router, prefix="/api/v1")
add_pagination(app_v1)