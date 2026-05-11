from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv
from app.models import *

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
def init_db():
    """Инициализирует структуру БД на основе SQLModel-метаданных.
    Создает отсутствующие таблицы при старте приложения.
    """
    print(DATABASE_URL)
    SQLModel.metadata.create_all(engine)

def close_db():
    """Закрывает соединения с базой данных.
    Освобождает ресурсы SQLAlchemy engine.
    """
    engine.dispose()
def get_engine():
    """Возвращает общий экземпляр SQLAlchemy engine.
    Используется в инфраструктурных зависимостях.
    """
    return engine
init_db()