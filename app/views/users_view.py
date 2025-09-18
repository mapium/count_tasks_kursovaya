from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
# Создаем объект хэшера с параметрами по умолчанию
ph = PasswordHasher()
def reg():
    while True:
        print('''Добро пожаловать! Выберите пункт меню:
        1. Регистрация
        2. Вход
        3. Выход''')
        user_input = input()
        if user_input == '1':
            print("Введите логин:")
            login = input()
            print("Введите пароль:")
            # Хеширование пароля
            password = input()
            hashed_password = ph.hash(password)
            
        print(f"Хэш пароля: {hashed_password}")
        # Проверка пароля
        try:
        # True если пароль совпадает с хэшем
            ph.verify(hashed_password, password)
            print("Пароль подтвержден")
        except VerifyMismatchError:
            print("Пароль не совпадает")