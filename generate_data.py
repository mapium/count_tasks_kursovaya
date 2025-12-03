"""
Скрипт для генерации тестовых данных с помощью Faker
"""
import random
from datetime import date, timedelta
from faker import Faker
from faker.providers import BaseProvider
from argon2 import PasswordHasher
from sqlmodel import Session, select
from app.db.database import engine, init_db
from app.models.roles import Roles
from app.models.task_status import Task_Status
from app.models.departments_model import Departments
from app.models.users import Users
from app.models.employee_models import Employees
from app.models.tasks import Tasks

# Инициализация Faker с русской локалью
fake = Faker('ru_RU')
ph = PasswordHasher()

# Кастомный провайдер для генерации российских данных
class RussianProvider(BaseProvider):
    def passport_series_number(self):
        """Генерирует серию и номер паспорта (10 цифр)"""
        return f"{random.randint(1000, 9999)}{random.randint(100000, 999999)}"
    
    def inn(self):
        """Генерирует ИНН (12 цифр)"""
        return f"{random.randint(100000000000, 999999999999)}"
    
    def snils(self):
        """Генерирует СНИЛС (11 цифр)"""
        return f"{random.randint(10000000000, 99999999999)}"
    
    def priority(self):
        """Генерирует приоритет задачи"""
        return random.choice(["малый", "средний", "высокий"])

fake.add_provider(RussianProvider)


def generate_roles(session: Session):
    """Генерация ролей"""
    print("Генерация ролей...")
    roles_data = [
        {"name": "admin", "description": "Администратор системы. Полный доступ ко всем функциям."},
        {"name": "manager", "description": "Руководитель подразделения. Управление своим отделом."},
        {"name": "employee", "description": "Сотрудник. Может работать только со своими задачами."},
    ]
    
    for role_data in roles_data:
        existing = session.exec(select(Roles).where(Roles.name == role_data["name"])).first()
        if not existing:
            role = Roles(**role_data)
            session.add(role)
    
    session.commit()
    print("Роли созданы")
    return session.exec(select(Roles)).all()


def generate_task_statuses(session: Session):
    """Генерация статусов задач"""
    print("Генерация статусов задач")
    statuses_data = [
        {"name": "К выполнению", "order_index": 1},
        {"name": "В работе", "order_index": 2},
        {"name": "На проверке", "order_index": 3},
        {"name": "Выполнено", "order_index": 4},
    ]
    
    for status_data in statuses_data:
        existing = session.exec(select(Task_Status).where(Task_Status.name == status_data["name"])).first()
        if not existing:
            status = Task_Status(**status_data)
            session.add(status)
    
    session.commit()
    print("Статусы задач созданы")
    return session.exec(select(Task_Status)).all()


def generate_departments(session: Session, count: int = 5):
    """Генерация отделов"""
    print(f"Генерация {count} отделов")
    departments = []
    
    department_names = [
        "Отдел разработки",
        "Отдел тестирования",
        "Отдел продаж",
        "Отдел маркетинга",
        "HR отдел",
        "Финансовый отдел",
        "Отдел поддержки",
        "Отдел безопасности",
    ]
    
    for i in range(count):
        name = department_names[i] if i < len(department_names) else fake.company()
        description = fake.text(max_nb_chars=200)
        
        department = Departments(
            name=name,
            description=description
        )
        session.add(department)
        departments.append(department)
    
    session.commit()
    session.refresh(departments[-1])
    print(f"Создано {count} отделов")
    return session.exec(select(Departments)).all()


def generate_users(session: Session, roles: list, count: int = 20):
    """Генерация пользователей"""
    print(f"Генерация {count} пользователей")
    users = []
    
    # Первый пользователь - админ (если еще не существует)
    admin_role = next((r for r in roles if r.name == "admin"), None)
    if admin_role:
        existing_admin = session.exec(select(Users).where(Users.username == "admin")).first()
        if not existing_admin:
            admin_user = Users(
                username="admin",
                password=ph.hash("admin123"),
                role_id=admin_role.id
            )
            session.add(admin_user)
            users.append(admin_user)
            count -= 1
        else:
            users.append(existing_admin)
            count -= 1
    
    # Генерация остальных пользователей
    manager_role = next((r for r in roles if r.name == "manager"), None)
    employee_role = next((r for r in roles if r.name == "employee"), None)
    
    for i in range(count):
        username = fake.user_name() + str(random.randint(100, 999))
        password = ph.hash("password123")  # Все имеют одинаковый пароль для тестирования
        
        # Распределение ролей: 20% менеджеры, 80% сотрудники
        if i < count * 0.2 and manager_role:
            role_id = manager_role.id
        else:
            role_id = employee_role.id if employee_role else roles[-1].id
        
        user = Users(
            username=username,
            password=password,
            role_id=role_id
        )
        session.add(user)
        users.append(user)
    
    session.commit()
    print(f"Создано {len(users)} пользователей")
    return session.exec(select(Users)).all()


def generate_employees(session: Session, users: list, departments: list, count: int = 20):
    """Генерация сотрудников"""
    print(f"Генерация {count} сотрудников")
    employees = []
    
    for i in range(min(count, len(users))):
        user = users[i] if i < len(users) else random.choice(users)
        
        # Проверяем, нет ли уже сотрудника для этого пользователя
        existing_employee = session.exec(select(Employees).where(Employees.user_id == user.id)).first()
        if existing_employee:
            employees.append(existing_employee)
            continue
        
        employee = Employees(
            user_id=user.id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            middle_name=fake.middle_name() if random.choice([True, False]) else None,
            phone_number=f"+7{random.randint(9000000000, 9999999999)}",
            email=fake.unique.email(),
            passport_data=fake.passport_series_number(),
            inn=fake.inn() if random.choice([True, False]) else None,
            snils=fake.snils() if random.choice([True, False]) else None,
            department_id=random.choice(departments).id,
            is_active=random.choice([True, True, True, False])  # 75% активных
        )
        session.add(employee)
        employees.append(employee)
    
    session.commit()
    print(f"Создано {len(employees)} сотрудников")
    return session.exec(select(Employees)).all()


def generate_tasks(session: Session, users: list, departments: list, statuses: list, count: int = 50):
    """Генерация задач"""
    print(f"Генерация {count} задач")
    tasks = []
    
    priorities = ["малый", "средний", "высокий"]
    
    for i in range(count):
        today = date.today()
        planned_start = today + timedelta(days=random.randint(-30, 30))
        planned_end = planned_start + timedelta(days=random.randint(1, 60))
        
        # Для некоторых задач добавляем фактические даты
        actual_start = None
        actual_end = None
        if random.choice([True, False]):
            actual_start = planned_start + timedelta(days=random.randint(0, 5))
            if random.choice([True, False]):
                actual_end = actual_start + timedelta(days=random.randint(1, 30))
        
        task = Tasks(
            title=fake.sentence(nb_words=4),
            description=fake.text(max_nb_chars=200),
            creator_id=random.choice(users).id,
            assignee_id=random.choice(users).id,
            department_id=random.choice(departments).id,
            status_id=random.choice(statuses).id,
            priority=random.choice(priorities),
            planned_start_date=planned_start,
            planned_end_date=planned_end,
            actual_start_date=actual_start,
            actual_end_date=actual_end
        )
        session.add(task)
        tasks.append(task)
    
    session.commit()
    print(f"✓ Создано {len(tasks)} задач")
    return tasks


def main():
    """Основная функция генерации данных"""
    print("=" * 50)
    print("Генерация тестовых данных с помощью Faker")
    print("=" * 50)
    
    # Инициализация БД
    init_db()
    
    with Session(engine) as session:
        try:
            # Генерация базовых данных
            roles = generate_roles(session)
            statuses = generate_task_statuses(session)
            departments = generate_departments(session, count=5)
            users = generate_users(session, roles, count=20)
            employees = generate_employees(session, users, departments, count=20)
            tasks = generate_tasks(session, users, departments, statuses, count=50)
            
            print("\n" + "=" * 50)
            print("Генерация данных завершена успешно!")
            print("=" * 50)
            print(f"\nСоздано:")
            print(f"  - Ролей: {len(roles)}")
            print(f"  - Статусов задач: {len(statuses)}")
            print(f"  - Отделов: {len(departments)}")
            print(f"  - Пользователей: {len(users)}")
            print(f"  - Сотрудников: {len(employees)}")
            print(f"  - Задач: {len(tasks)}")
            print(f"\nДанные для входа:")
            print(f"  Администратор:")
            print(f"    Username: admin")
            print(f"    Password: admin123")
            print(f"\n  Остальные пользователи:")
            print(f"    Username: <любой сгенерированный username>")
            print(f"    Password: password123  ⚠️ (НЕ username123!)")
            print(f"\n  Примеры сгенерированных пользователей:")
            all_users = session.exec(select(Users)).all()
            example_count = 0
            for user in all_users:
                if user.username != "admin" and example_count < 5:
                    print(f"    - Username: {user.username}")
                    print(f"      Password: password123")
                    example_count += 1
            print("\nВсе пользователи (кроме админа) имеют одинаковый пароль: password123")
            print("=" * 50)
            
        except Exception as e:
            session.rollback()
            print(f"\nОшибка при генерации данных: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    main()

