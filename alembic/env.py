from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv
from sqlmodel import SQLModel

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.database import get_engine
from app.models import *

# Добавляем переменные окружения
load_dotenv()

# Берем настройки подключения к СУБД из конфигурационного файла alembic.ini
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
  # задаем параметр подключения к базе данных из переменных окруженя
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        url = config.get_main_option("sqlalchemy.url",database_url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()