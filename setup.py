#!/usr/bin/env python3
"""
Скрипт для установки зависимостей и настройки проекта
"""

import subprocess
import sys
import os

def install_requirements():
    """Установка зависимостей из requirements.txt"""
    print("Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Зависимости успешно установлены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def create_env_file():
    """Создание файла .env из примера"""
    if not os.path.exists('.env'):
        if os.path.exists('config.env.example'):
            try:
                with open('config.env.example', 'r', encoding='utf-8') as src:
                    content = src.read()
                with open('.env', 'w', encoding='utf-8') as dst:
                    dst.write(content)
                print("✅ Файл .env создан из config.env.example")
                print("⚠️  Не забудьте отредактировать файл .env с вашими настройками PostgreSQL!")
                return True
            except Exception as e:
                print(f"❌ Ошибка создания файла .env: {e}")
                return False
        else:
            print("❌ Файл config.env.example не найден")
            return False
    else:
        print("ℹ️  Файл .env уже существует")
        return True

def main():
    """Основная функция настройки"""
    print("Настройка проекта для работы с PostgreSQL...")
    print("=" * 50)
    
    # Установка зависимостей
    if not install_requirements():
        sys.exit(1)
    
    print()
    
    # Создание файла .env
    if not create_env_file():
        sys.exit(1)
    
    print()
    print("🎉 Настройка завершена!")
    print()
    print("Следующие шаги:")
    print("1. Установите PostgreSQL")
    print("2. Создайте базу данных: CREATE DATABASE count_tasks;")
    print("3. Отредактируйте файл .env с вашими настройками")
    print("4. Запустите: python init_db.py")
    print("5. Запустите приложение: python app/main.py")

if __name__ == "__main__":
    main()

