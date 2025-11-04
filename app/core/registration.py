from app.controllers.users_controller import register_user, authorize_user

def reg():
    while True:
        print('''Добро пожаловать! Выберите пункт меню:
        1. Вход
        2. Регистрация
        3. Выход''')

        user_input = input()
        if user_input == '1':
            print('Введите логин:')
            login = input()
            print('Введите пароль:')
            password = input()
            if authorize_user(login, password):
                print('Вы вошли в систему')
                return True
            else:
                print('Неверный логин или пароль')

        elif user_input == '2':
            print('Введите логин:')
            login = input()
            print('Введите пароль:')
            password = input()
            print('Повторите пароль:')
            password_repeat = input()
            if password != password_repeat:
                print('Пароли не совпадают!')
                continue
            if register_user(login, password):
                print('Регистрация прошла успешно!')
            else:
                print('Пользователь с таким логином уже существует')

        elif user_input == '3':
            print('Завершение работы')
            break