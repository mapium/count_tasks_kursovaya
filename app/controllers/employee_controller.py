import sqlite3
from db.database import conn, cursor


def add_employee(first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id):
    """
    Добавление нового сотрудника
    """
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employees (first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding employee: {e}")
        return False


def get_all_employees():
    """
    Получение всех сотрудников
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting employees: {e}")
        return []


def edit_department_id(employee_id, new_department_id):
    """
    Редактирование department_id у сотрудника
    """
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE employees SET department_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_department_id, employee_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error editing department_id: {e}")
        return False