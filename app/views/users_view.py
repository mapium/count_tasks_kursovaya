def show_auth_menu():
    print('''Добро пожаловать! Выберите пункт меню:
        1. Вход
        2. Регистрация
        3. Выход''')
    return input().strip()


def prompt_login_credentials():
    print('Введите логин:')
    username = input().strip()
    print('Введите пароль:')
    password = input()
    return username, password


def prompt_register_credentials():
    print('Введите логин:')
    username = input().strip()
    print('Введите пароль:')
    password = input()
    print('Повторите пароль:')
    password_repeat = input()
    return username, password, password_repeat


def show_login_result(success: bool):
    if success:
        print('Вы вошли в систему')
    else:
        print('Неверный логин или пароль')


def show_register_result(success: bool):
    if success:
        print('Регистрация прошла успешно!')
    else:
        print('Пользователь с таким логином уже существует')