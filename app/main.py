from db.database import init_db
from views.employee_view import (
    add_employee as view_add_employee,
    add_employee_result,
    input_delete_employee,
    delete_employee_result,
    display_all_employees,
    edit_employee_dep_id,
    edit_employee_dep_id_result,
)
from controllers.employee_controller import (
    add_employee as controller_add_employee,
    get_all_employees,
    edit_department_id,
    del_employee,
)
from registration import reg


def main():
    init_db()
    if not reg():
        return
    while True:
        print("\nMenu:")
        print("1. Add employee")
        print("2. Get all employees")
        print("3. Edit department id employee")
        print("4. Delete employee")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id = view_add_employee()
            success = controller_add_employee(first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id)
            add_employee_result(success)
        elif choice == "2":
            employees = get_all_employees()
            display_all_employees(employees)
        elif choice == "3":
            employee_id, new_department_id = edit_employee_dep_id()
            success = edit_department_id(employee_id, new_department_id)
            edit_employee_dep_id_result(success)
        elif choice == "4":
            del_employee_id = input_delete_employee()
            success = del_employee(del_employee_id)
            delete_employee_result(success)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()