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
        # employee: экземпляр модели Employees (SQLModel)
        id_val = getattr(employee, 'id', '') or ''
        first_name = getattr(employee, 'first_name', '') or ''
        last_name = getattr(employee, 'last_name', '') or ''
        middle_name = getattr(employee, 'middle_name', '') or ''
        phone_number = getattr(employee, 'phone_number', '') or ''
        email = getattr(employee, 'email', '') or ''
        passport_data = getattr(employee, 'passport_data', '') or ''
        inn = getattr(employee, 'inn', '') or ''
        snils = getattr(employee, 'snils', '') or ''
        department_id = getattr(employee, 'department_id', '') or ''
        
        print(f"{id_val:<5} {first_name:<15} {last_name:<15} {middle_name:<15} {email:<25} {phone_number:<15} {passport_data:<15} {inn:<15} {snils:<15} {department_id:<8}")
    
    print(f"\nВсего сотрудников: {len(employees)}")

def edit_employee_dep_id():
    """
    Ввод идентификаторов для смены department_id у сотрудника
    """
    employee_id = input("Введите id сотрудника: ").strip()
    new_department_id = input("Введите новый department id: ").strip()
    return employee_id, new_department_id

def edit_employee_dep_id_result(success: bool):
    if success:
        print("Department id успешно обновлен")
    else:
        print("Не удалось обновить department id")

def input_delete_employee():
    employee_id = input("Введите ID сотрудника, которого необходимо удалить: ").strip()
    return employee_id

def delete_employee_result(success: bool):
    if success:
        print("Сотрудник успешно удалён")
    else:
        print("Не удалось удалить сотрудника")