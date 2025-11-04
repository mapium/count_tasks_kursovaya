from app.db.database import init_db, close_db
from app.api.v1.employee_router import router
from app.controllers.employee_controller import *
from app.core.registration import reg
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
from typing import Annotated
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@asynccontextmanager
async def on_startup(app: FastAPI):
    init_db()
    yield
    close_db()

app_v1 = FastAPI(lifespan=on_startup)
@app_v1.get("/api/v1/auth")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
app_v1.include_router(router, prefix="/api/v1")


# def main():
#     init_db()
    # if not reg():
    #     return
    # while True:
    #     print("\nMenu:")
    #     print("1. Add employee")
    #     print("2. Get all employees")
    #     print("3. Edit department id employee")
    #     print("4. Delete employee")
    #     print("5. Exit")
    #     choice = input("Enter your choice: ")
    #     if choice == "1":
    #         first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id = view_add_employee()
    #         success = controller_add_employee(first_name, last_name, middle_name, phone_number, email, passport_data, inn, snils, department_id)
    #         add_employee_result(success)
    #     elif choice == "2":
    #         employees = get_all_employees()
    #         display_all_employees(employees)
    #     elif choice == "3":
    #         employee_id, new_department_id = edit_employee_dep_id()
    #         success = edit_department_id(employee_id, new_department_id)
    #         edit_employee_dep_id_result(success)
    #     elif choice == "4":
    #         del_employee_id = input_delete_employee()
    #         success = del_employee(del_employee_id)
    #         delete_employee_result(success)
    #     elif choice == "5":
    #         print("Goodbye!")
    #         break
    #     else:
    #         print("Invalid choice")


# if __name__ == "__main__":
#     main()