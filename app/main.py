from db.database import init_db
from views.employee_view import add_employee, add_employee_result, display_all_employees
from controllers import employee_controller


def main():
    init_db()
    while True:
        print("\nMenu:")
        print("1. Add employee")
        print("2. Get all employees")
        print("3. Add department")
        print("4. Add task")
        print("5. Add user")
        print("6. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id = add_employee()
            success = employee_controller.add_employee(first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id)
            add_employee_result(success)
        elif choice == "2":
            employees = employee_controller.get_all_employees()
            display_all_employees(employees)
        elif choice == "3":
            pass
        elif choice == "4":
            pass
        elif choice == "5":
            pass
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()