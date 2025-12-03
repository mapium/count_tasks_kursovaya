# Генерация тестовых данных с помощью Faker

Этот скрипт позволяет автоматически заполнить базу данных тестовыми данными для разработки и тестирования.

## Установка

1. Убедитесь, что все зависимости установлены:
```bash
pip install -r requirements.txt
```

2. Скрипт автоматически установит Faker при установке зависимостей.

## Использование

### Запуск генерации данных

```bash
python generate_data.py
```

### Что генерируется

Скрипт создает следующие данные:

1. **Роли** (3 роли):
   - admin (Администратор)
   - manager (Руководитель отдела)
   - employee (Сотрудник)

2. **Статусы задач** (4 статуса):
   - К выполнению
   - В работе
   - На проверке
   - Выполнено

3. **Отделы** (5 отделов):
   - Отдел разработки
   - Отдел тестирования
   - Отдел продаж
   - Отдел маркетинга
   - HR отдел

4. **Пользователи** (20 пользователей):
   - 1 администратор (username: `admin`, password: `admin123`)
   - ~4 менеджера (password: `password123`)
   - ~15 сотрудников (password: `password123`)
   - ⚠️ **Важно**: Все остальные пользователи имеют одинаковый пароль: `password123`

5. **Сотрудники** (20 сотрудников):
   - Связь с пользователями
   - Полные ФИО
   - Телефоны, email
   - Паспортные данные, ИНН, СНИЛС
   - Привязка к отделам

6. **Задачи** (50 задач):
   - Название и описание
   - Создатель и исполнитель
   - Отдел и статус
   - Приоритет (малый, средний, высокий)
   - Плановые и фактические даты

## Настройка количества данных

Вы можете изменить количество генерируемых данных в функции `main()`:

```python
departments = generate_departments(session, count=5)      # количество отделов
users = generate_users(session, roles, count=20)          # количество пользователей
employees = generate_employees(session, users, departments, count=20)  # количество сотрудников
tasks = generate_tasks(session, users, departments, statuses, count=50)  # количество задач
```

## Важные замечания

1. **Данные не удаляются**: Скрипт проверяет существование записей и не создает дубликаты для базовых данных (роли, статусы).

2. **Пароли**: 
   - Администратор: `admin` / `admin123`
   - Остальные пользователи: `<username>` / `password123`

3. **Зависимости**: Данные создаются в правильном порядке с учетом внешних ключей:
   - Сначала роли и статусы
   - Затем отделы
   - Потом пользователи
   - Затем сотрудники
   - И наконец задачи

## Примеры использования

### Генерация минимального набора данных

Измените в `main()`:
```python
departments = generate_departments(session, count=3)
users = generate_users(session, roles, count=10)
employees = generate_employees(session, users, departments, count=10)
tasks = generate_tasks(session, users, departments, statuses, count=20)
```

### Генерация большого набора данных

Измените в `main()`:
```python
departments = generate_departments(session, count=10)
users = generate_users(session, roles, count=100)
employees = generate_employees(session, users, departments, count=100)
tasks = generate_tasks(session, users, departments, statuses, count=500)
```

## Очистка данных

Для полной очистки данных используйте SQL или создайте отдельный скрипт:

```sql
TRUNCATE TABLE tasks CASCADE;
TRUNCATE TABLE employees CASCADE;
TRUNCATE TABLE users CASCADE;
TRUNCATE TABLE departments CASCADE;
TRUNCATE TABLE task_status CASCADE;
TRUNCATE TABLE roles CASCADE;
```

⚠️ **Внимание**: Будьте осторожны при очистке данных в продакшн среде!

## Особенности генерации

- **Faker использует русскую локаль** (`ru_RU`) для генерации реалистичных русских имен, адресов и текста
- **Уникальные поля** автоматически проверяются (email, username, passport_data)
- **Даты задач** генерируются с учетом логики (плановая дата окончания после даты начала)
- **Связи между таблицами** устанавливаются корректно

