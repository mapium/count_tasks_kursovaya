#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных PostgreSQL
"""

import sys
import os

# Добавляем путь к приложению
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from db.database import init_db

def main():
    """Инициализация базы данных"""
    print("Инициализация базы данных PostgreSQL...")
    
    conn, cursor = init_db()
    
    if conn and cursor:
        print("✅ База данных успешно инициализирована!")
        print("Теперь вы можете запустить приложение: python app/main.py")
    else:
        print("❌ Ошибка инициализации базы данных")
        print("Проверьте:")
        print("1. Установлен ли PostgreSQL")
        print("2. Создана ли база данных 'count_tasks'")
        print("3. Правильно ли настроены переменные окружения в файле .env")
        sys.exit(1)

if __name__ == "__main__":
    main()

