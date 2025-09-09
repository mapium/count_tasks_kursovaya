import sqlite3

def init_db():
    """
    Подключение к БД
    :return: conn - подключение, cursor - курсор
    """
    try:
        conn = sqlite3.connect("../count_tasks_kursovaya/app/db/count_tasks.db")
        cursor = conn.cursor()
        # Проверяем подключение
        cursor.execute("SELECT 1")
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            middle_name TEXT,
            phone_number TEXT,
            email TEXT NOT NULL UNIQUE,
            passport_data TEXT NOT NULL UNIQUE,
            inn TEXT UNIQUE,
            snils TEXT UNIQUE,
            department_id INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            employee_id INTEGER NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS task_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            order_index INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            creator_id INTEGER NOT NULL,
            assignee_id INTEGER,
            department_id INTEGER NOT NULL,
            status_id INTEGER NOT NULL,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
            planned_start_date DATE,
            planned_end_date DATE NOT NULL,
            actual_start_date DATE,
            actual_end_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES employees(id) ON DELETE RESTRICT,
            FOREIGN KEY (assignee_id) REFERENCES employees(id) ON DELETE SET NULL,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
            FOREIGN KEY (status_id) REFERENCES task_statuses(id) ON DELETE RESTRICT
        );
        CREATE TABLE IF NOT EXISTS task_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            comment_text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES employees(id) ON DELETE RESTRICT
        );
        ''')
        # Создание индексов
        cursor.executescript('''
        CREATE INDEX IF NOT EXISTS idx_employees_last_name ON employees (last_name);
        CREATE INDEX IF NOT EXISTS idx_tasks_assignee_status ON tasks(assignee_id, status_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_department_status ON tasks(department_id, status_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_planned_end_date ON tasks(planned_end_date);
        
        CREATE INDEX IF NOT EXISTS idx_tasks_actual_end_date ON tasks(actual_end_date);
        CREATE INDEX IF NOT EXISTS idx_employees_department_id ON employees(department_id);
        ''')
        
        # Заполнение начальных данных
        cursor.executescript('''
        INSERT OR IGNORE INTO task_statuses (name, order_index) VALUES
        ('К выполнению', 1),
        ('В работе', 2),
        ('На проверке', 3),
        ('Выполнено', 4);

        INSERT OR IGNORE INTO roles (name, description) VALUES
        ('admin', 'Администратор системы. Полный доступ ко всем функциям.'),
        ('ceo', 'Руководитель предприятия. Полный доступ к просмотру и отчетам.'),
        ('manager', 'Руководитель подразделения. Управление своим отделом.'),
        ('employee', 'Сотрудник. Может работать только со своими задачами.');
        ''')
        conn.commit()
        print("База данных инициализирована успешно!")
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Ошибка инициализации базы данных: {e}")
        return None, None


# Создание подключения  и курсора
conn, cursor = init_db()
if conn and cursor:
    print("Можно продолжать работу")
else:
    print("Не удалось подключиться к базе данных")
