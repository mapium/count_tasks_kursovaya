from db.database import conn, cursor

def add_employee():
    """
    Добавление сотрудника
    """
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    middle_name = input("Enter middle name: ")
    phone_number = input("Enter phone number: ")
    email = input("Enter email: ")
    passport_data = input("Enter passport data: ")
    inn = input("Enter inn: ")
    snils = input("Enter snils: ")
    department_id = input("Enter department id: ")
    return first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id
def add_employee_result(success: bool):
    if success:
        print("Employee added successfully")
    else:
        print("Employee addition failed")
def display_all_employees(employees):
    """
    Отображение всех сотрудников
    """
    if not employees:
        print("Сотрудники не найдены")
        return
    
    print("=" * 65, "СПИСОК СОТРУДНИКОВ", "=" * 65)
    print(f"{'ID':<5} {'Имя':<15} {'Фамилия':<15} {'Отчество':<15} {'Email':<25} {'Телефон':<15} {'Паспорт':<15} {'ИНН':<15} {'СНИЛС':<15} {'Отдел':<8}")
    print("=" * 150)
    
    for employee in employees:
        # employee структура: (id, user_id, first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id, is_active, created_at, updated_at)
        id_val = employee[0] or ''
        first_name = employee[2] or ''
        last_name = employee[3] or ''
        middle_name = employee[4] or ''
        phone_number = employee[5] or ''
        email = employee[6] or ''
        passport_data = employee[7] or ''
        inn = employee[8] or ''
        snils = employee[9] or ''
        department_id = employee[10] or ''
        
        print(f"{id_val:<5} {first_name:<15} {last_name:<15} {middle_name:<15} {email:<25} {phone_number:<15} {passport_data:<15} {inn:<15} {snils:<15} {department_id:<8}")
    
    print(f"\nВсего сотрудников: {len(employees)}")
    