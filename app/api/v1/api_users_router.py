from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlmodel import Session

from app.controllers.users_controller import (
    admin_registration,
    change_my_password,
    delete_user_by_admin,
    get_users,
    login,
    refresh_access_token,
    registration,
    update_user_by_admin,
)
from app.core.security import admin_required, get_current_user
from app.db.session import get_session
from app.models.users import Users
from app.schemas.user_schema import (
    UserLogin,
    UserPasswordChange,
    UserSchema,
    UserSchemaCreate as USC,
    UserSchemaCreateAsAdmin,
    UserUpdateAsAdmin,
)

router = APIRouter()


@router.post(
    "/accounts/sign_up_as_admin",
    tags=["Регистрация, авторизация"],
    description="Только с правами администратора",
    summary="Зарегистрировать пользователя администратором",
)
def admin_registration_route(
    form_data: UserSchemaCreateAsAdmin = Depends(UserSchemaCreateAsAdmin.as_form),
    user: Users = Depends(admin_required),
    session: Session = Depends(get_session),
):
    return admin_registration(form_data, user, session)


@router.post("/accounts/sign_up", tags=["Регистрация, авторизация"], summary="Регистрация")
def registration_route(form_data: UserSchema = Depends(USC.as_form), session: Session = Depends(get_session)):
    return registration(form_data, session)


@router.post("/auth/login", tags=["Регистрация, авторизация"], summary="Авторизация")
def login_route(form_data: UserLogin = Depends(UserLogin.as_form), session: Session = Depends(get_session)):
    return login(form_data, session)


@router.post("/auth/refresh", tags=["Регистрация, авторизация"], summary="Обновить токен")
def refresh_token_route(refresh_token: str):
    return refresh_access_token(refresh_token)


@router.get(
    "/users",
    response_model=Page[Users],
    tags=["Регистрация, авторизация"],
    description="Только с правами администратора",
    summary="Список всех пользователей",
)
def users_list_route(current_user: Users = Depends(admin_required), session: Session = Depends(get_session)):
    return get_users(current_user, session)


@router.get("/users/me", response_model=Users, tags=["Регистрация, авторизация"], summary="Текущий пользователь")
def current_user_route(current_user: Users = Depends(get_current_user)):
    return current_user


@router.post("/users/me/change-password", tags=["Регистрация, авторизация"], summary="Сменить свой пароль")
def change_my_password_route(
    form_data: UserPasswordChange = Depends(UserPasswordChange.as_form),
    current_user: Users = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return change_my_password(form_data, current_user, session)


@router.put(
    "/users/{id}",
    response_model=Users,
    tags=["Регистрация, авторизация"],
    description="Только с правами администратора",
    summary="Обновить пользователя",
)
def update_user_route(
    id: int,
    form_data: UserUpdateAsAdmin = Depends(UserUpdateAsAdmin.as_form),
    current_user: Users = Depends(admin_required),
    session: Session = Depends(get_session),
):
    return update_user_by_admin(id, form_data, current_user, session)


@router.delete(
    "/users/{id}",
    tags=["Регистрация, авторизация"],
    description="Только с правами администратора",
    summary="Удалить пользователя",
)
def delete_user_route(
    id: int,
    current_user: Users = Depends(admin_required),
    session: Session = Depends(get_session),
):
    return delete_user_by_admin(id, current_user, session)
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlmodel import Session

from app.controllers.users_controller import login, refresh_access_token, get_users, admin_registration, registration, update_user_by_admin, delete_user_by_admin, change_my_password
from app.core.security import get_current_user, admin_required
from app.db.session import get_session
from app.models.users import Users
from app.schemas.user_schema import UserSchema, UserSchemaCreateAsAdmin, UserSchemaCreate as USC, UserLogin, UserUpdateAsAdmin, UserPasswordChange

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

@router.get("/users/me", response_model=Users, tags=["Регистрация, авторизация"], summary="Текущий пользователь")
def current_user_route(current_user: Users = Depends(get_current_user)):
    return current_user


@router.post("/users/me/change-password", tags=["Регистрация, авторизация"], summary="Сменить свой пароль")
def change_my_password_route(
    form_data: UserPasswordChange = Depends(UserPasswordChange.as_form),
    current_user: Users = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return change_my_password(form_data, current_user, session)


@router.put("/users/{id}", response_model=Users, tags=["Регистрация, авторизация"], description="Только с правами администратора", summary="Обновить пользователя")
def update_user_route(
    id: int,
    form_data: UserUpdateAsAdmin = Depends(UserUpdateAsAdmin.as_form),
    current_user: Users = Depends(admin_required),
    session: Session = Depends(get_session),
):
    return update_user_by_admin(id, form_data, current_user, session)


@router.delete("/users/{id}", tags=["Регистрация, авторизация"], description="Только с правами администратора", summary="Удалить пользователя")
def delete_user_route(
    id: int,
    current_user: Users = Depends(admin_required),
    session: Session = Depends(get_session),
):
    return delete_user_by_admin(id, current_user, session)