from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv
from models.users_model import Users
from models.employee_models import Employees
from models.departments_model import Departments

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    print(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
init_db()

#         # Проверяем подключение
#         cursor.execute("SELECT 1")
        
#         # Создание таблиц
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS departments (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(255) NOT NULL UNIQUE,
#             description TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         ''')
        
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS employees (
#             id SERIAL PRIMARY KEY,
#             user_id INTEGER UNIQUE,
#             first_name VARCHAR(255) NOT NULL,
#             last_name VARCHAR(255) NOT NULL,
#             middle_name VARCHAR(255),
#             phone_number VARCHAR(20),
#             email VARCHAR(255) NOT NULL UNIQUE,
#             passport_data VARCHAR(255) NOT NULL UNIQUE,
#             inn VARCHAR(12) UNIQUE,
#             snils VARCHAR(11) UNIQUE,
#             department_id INTEGER NOT NULL,
#             is_active BOOLEAN DEFAULT TRUE,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT
#         );
#         ''')
#         # CREATE TABLE IF NOT EXISTS users (
#         #     id SERIAL PRIMARY KEY,
#         #     username VARCHAR(255) UNIQUE NOT NULL,
#         #     password_hash VARCHAR(255) NOT NULL,
#         #     employee_id INTEGER UNIQUE,
#         #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         #     last_login TIMESTAMP,
#         #     FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
#         # );
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id SERIAL PRIMARY KEY,
#             username character varying(50) UNIQUE NOT NULL,
#             password_hash character varying(200) NOT NULL
#         );
#         ''')
        
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS roles (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(255) NOT NULL UNIQUE,
#             description TEXT
#         );
#         ''')
        
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS user_roles (
#             user_id INTEGER NOT NULL,
#             role_id INTEGER NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             PRIMARY KEY (user_id, role_id),
#             FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
#             FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
#         );
#         ''')
        
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS task_statuses (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(255) NOT NULL UNIQUE,
#             order_index INTEGER NOT NULL
#         );
#         ''')
        
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS tasks (
#             id SERIAL PRIMARY KEY,
#             title VARCHAR(255) NOT NULL,
#             description TEXT,
#             creator_id INTEGER NOT NULL,
#             assignee_id INTEGER,
#             department_id INTEGER NOT NULL,
#             status_id INTEGER NOT NULL,
#             priority VARCHAR(10) DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
#             planned_start_date DATE,
#             planned_end_date DATE NOT NULL,
#             actual_start_date DATE,
#             actual_end_date DATE,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (creator_id) REFERENCES employees(id) ON DELETE RESTRICT,
#             FOREIGN KEY (assignee_id) REFERENCES employees(id) ON DELETE SET NULL,
#             FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
#             FOREIGN KEY (status_id) REFERENCES task_statuses(id) ON DELETE RESTRICT
#         );
#         ''')
        
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS task_comments (
#             id SERIAL PRIMARY KEY,
#             task_id INTEGER NOT NULL,
#             author_id INTEGER NOT NULL,
#             comment_text TEXT NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
#             FOREIGN KEY (author_id) REFERENCES employees(id) ON DELETE RESTRICT
#         );
#         ''')
        
#         # Создание индексов
#         cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_last_name ON employees (last_name);')
#         cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_assignee_status ON tasks(assignee_id, status_id);')
#         cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_department_status ON tasks(department_id, status_id);')
#         cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_planned_end_date ON tasks(planned_end_date);')
#         cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_actual_end_date ON tasks(actual_end_date);')
#         cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_department_id ON employees(department_id);')
        
#         # Заполнение начальных данных
#         cursor.execute('''
#         INSERT INTO task_statuses (name, order_index) VALUES
#         ('К выполнению', 1),
#         ('В работе', 2),
#         ('На проверке', 3),
#         ('Выполнено', 4)
#         ON CONFLICT (name) DO NOTHING;
#         ''')
        
#         cursor.execute('''
#         INSERT INTO roles (name, description) VALUES
#         ('admin', 'Администратор системы. Полный доступ ко всем функциям.'),
#         ('ceo', 'Руководитель предприятия. Полный доступ к просмотру и отчетам.'),
#         ('manager', 'Руководитель подразделения. Управление своим отделом.'),
#         ('employee', 'Сотрудник. Может работать только со своими задачами.')
#         ON CONFLICT (name) DO NOTHING;
#         ''')
        
#         conn.commit()
#         print("База данных PostgreSQL инициализирована успешно!")
#         return conn, cursor
#     except psycopg2.Error as e:
#         print(f"Ошибка инициализации базы данных PostgreSQL: {e}")
#         return None, None


# # Создание подключения и курсора
# conn, cursor = init_db()
# if conn and cursor:
#     print("Можно продолжать работу")
# else:
#     print("Не удалось подключиться к базе данных")
