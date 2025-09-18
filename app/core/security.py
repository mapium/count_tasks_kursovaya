from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Инициализация хэшера Argon2
ph = PasswordHasher()
def hash_data(data:str)->str:
    """
        Хэширование данных
        :param data: данные в открытом виде
        :return:  безопасный хэш с помощью argon2
        """
    return ph.hash(data)

def verify_data(plain_data: str, hashed_data: str) -> bool:
    """"
            Проверка данных (Сравнивает введённые данные с сохранённым хэшем, чтобы проверить соответствие)
            :param plain_data: данные в открытом виде
            :param hashed_data: ранее сохранённый хэш данных
            :return: True, если  совпадают
            """
    try:
        ph.verify(hashed_data, plain_data)
        return True
    except VerifyMismatchError:
        return False
