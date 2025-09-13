import psycopg2
from psycopg2.extras import RealDictCursor
from db.database import conn, cursor


def add_employee(first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id):
    """
    Добавление нового сотрудника
    """
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO employees (first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Error adding employee: {e}")
        return False


def get_all_employees():
    """
    Получение всех сотрудников
    """
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM employees ORDER BY id")
        return cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error getting employees: {e}")
        return []


def edit_department_id(employee_id, new_department_id):
    """
    Редактирование department_id у сотрудника
    """
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            UPDATE employees 
            SET department_id = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (new_department_id, employee_id))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Error editing department_id: {e}")
        return False

def del_employee(employee_id):
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Ошибка удаления сотрудника: {e}")
        return False