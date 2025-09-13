# Система управления сотрудниками (PostgreSQL)

Система для управления сотрудниками с использованием PostgreSQL в качестве базы данных.

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка PostgreSQL

1. Установите PostgreSQL на вашем компьютере
2. Создайте базу данных:
```sql
CREATE DATABASE count_tasks;
```

### 3. Настройка переменных окружения

Скопируйте файл `config.env.example` в `.env` и настройте параметры подключения:

```bash
cp config.env.example .env
```

Отредактируйте файл `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=count_tasks
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Запуск приложения

```bash
python app/main.py
```

## Структура проекта

- `app/main.py` - главный файл приложения
- `app/db/database.py` - конфигурация базы данных PostgreSQL
- `app/models/` - модели данных
- `app/controllers/` - контроллеры для работы с данными
- `app/views/` - представления (пользовательский интерфейс)

## Функциональность

- Добавление сотрудников
- Просмотр всех сотрудников
- Редактирование отдела сотрудника
- Удаление сотрудников

## Требования

- Python 3.7+
- PostgreSQL 12+
- psycopg2-binary
- python-dotenv

