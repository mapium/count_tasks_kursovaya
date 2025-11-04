from app.db.database import engine
import psycopg2
from app.core.security import ph
from argon2.exceptions import VerifyMismatchError
from app.models.users_model import Users
from sqlmodel import Session, select

def register_user(username, password):
    username = username.strip()
    password_hash = ph.hash(password)
    with Session(engine) as session:
        user = Users(username=username, password_hash=password_hash)
        session.add(user)
        session.commit()
        return True

def authorize_user(username, password):
    username = username.strip()
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.username == username)).first()
        if user is None or user.password_hash is None:
            return False
        stored_hash = user.password_hash
        try:
            ph.verify(stored_hash, password)
            return True
        except VerifyMismatchError:
            return False