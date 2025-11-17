from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page
from sqlmodel import Session

from app.controllers.users_controller import login, refresh_access_token, get_users, admin_registration, registration
from app.core.security import get_current_user, admin_required
from app.db.session import get_session
from app.models.users import Users
from app.schemas.user_schema import UserSchema, UserSchemaCreateAsAdmin, UserSchemaCreate as USC

router = APIRouter()

@router.post("/accounts/sign_up_as_admin",tags=["auth"])
def sign_up_as_admin_route(
    form_data: UserSchemaCreateAsAdmin = Depends(UserSchemaCreateAsAdmin.as_form),
    user: Users = Depends(admin_required),
    session: Session = Depends(get_session)
):
    return admin_registration(form_data, user, session)

@router.post("/accounts/sign_up",tags=["auth"])
def sign_up(form_data: UserSchema=Depends(USC.as_form),session:Session=Depends(get_session)):
    return registration(form_data, session)

@router.post("/auth/login",tags=["auth"])
def login_route(form_data: UserSchema=Depends(UserSchema.as_form),session:Session=Depends(get_session)):
    return login(form_data,session)

@router.post("/auth/refresh",tags=["auth"])
def refresh_token_route(refresh_token:str):
    return refresh_access_token(refresh_token)

@router.get("/users", response_model=Page[Users],tags=["auth"])
def get_users_route(current_user: Users = Depends(admin_required),session: Session=Depends(get_session)):
        return  get_users(current_user,session)