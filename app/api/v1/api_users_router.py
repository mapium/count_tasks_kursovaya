from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlmodel import Session

from app.controllers.users_controller import login, refresh_access_token, get_users, admin_registration, registration
from app.core.security import get_current_user, admin_required
from app.db.session import get_session
from app.models.users import Users
from app.schemas.user_schema import UserSchema, UserSchemaCreateAsAdmin, UserSchemaCreate as USC, UserLogin

router = APIRouter()

@router.post("/accounts/sign_up_as_admin",tags=["Регистрация, авторизация"], description="Только с правами администратора", summary="Зарегистрировать пользователя администратором")
def admin_registration_route(
    form_data: UserSchemaCreateAsAdmin = Depends(UserSchemaCreateAsAdmin.as_form),
    user: Users = Depends(admin_required),
    session: Session = Depends(get_session)
):
    return admin_registration(form_data, user, session)

@router.post("/accounts/sign_up",tags=["Регистрация, авторизация"], summary="Регистрация")
def registration_route(form_data: UserSchema=Depends(USC.as_form),session:Session=Depends(get_session)):
    return registration(form_data, session)

@router.post("/auth/login",tags=["Регистрация, авторизация"], summary="Авторизация")
def login_route(form_data: UserLogin = Depends(UserLogin.as_form),session:Session=Depends(get_session)):
    return login(form_data,session)

@router.post("/auth/refresh",tags=["Регистрация, авторизация"], summary="Обновить токен")
def refresh_token_route(refresh_token:str):
    return refresh_access_token(refresh_token)

@router.get("/users", response_model=Page[Users],tags=["Регистрация, авторизация"], description="Только с правами администратора", summary="Список всех пользователей")
def users_list_route(current_user: Users = Depends(admin_required),session: Session=Depends(get_session)):
        return  get_users(current_user,session)