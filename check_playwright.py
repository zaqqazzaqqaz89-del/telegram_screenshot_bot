#!/usr/bin/env python3
"""
Скрипт диагностики Playwright
"""
import os
import sys
from pathlib import Path

def check_playwright():
    print("🔍 Проверка Playwright установки...\n")
    
    # Проверка переменных окружения
    print("📋 Переменные окружения:")
    browsers_path = os.getenv('PLAYWRIGHT_BROWSERS_PATH', 'Не установлено')
    print(f"  PLAYWRIGHT_BROWSERS_PATH: {browsers_path}")
    
    # Проверка директорий
    print("\n📁 Директории браузеров:")
    possible_paths = [
        '/opt/render/.cache/ms-playwright',
        '/home/claude/.cache/ms-playwright',
        os.path.expanduser('~/.cache/ms-playwright')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"  ✅ {path}")
            # Показываем содержимое
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    print(f"     - {item}")
                    if os.path.isdir(item_path):
                        try:
                            sub_items = os.listdir(item_path)
                            for sub in sub_items[:5]:  # Показываем первые 5
                                print(f"       • {sub}")
                        except:
                            pass
            except Exception as e:
                print(f"     ⚠️  Не удалось прочитать: {e}")
        else:
            print(f"  ❌ {path}")
    
    # Проверка импорта Playwright
    print("\n🐍 Python импорт:")
    try:
        from playwright.sync_api import sync_playwright
        print("  ✅ Playwright импортирован")
        
        # Проверка версии
        import playwright
        print(f"  📦 Версия: {playwright.__version__}")
    except Exception as e:
        print(f"  ❌ Ошибка импорта: {e}")
        return
    
    # Пробуем запустить браузер
    print("\n🌐 Попытка запуска браузера:")
    try:
        with sync_playwright() as p:
            print("  📌 Попытка 1: Стандартный запуск")
            try:
                browser = p.chromium.launch(headless=True)
                print("  ✅ Браузер запущен успешно!")
                browser.close()
            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
                
                # Показываем где Playwright ищет браузер
                print("\n  📍 Playwright ищет браузер здесь:")
                try:
                    # Пытаемся получить путь
                    executable_path = p.chromium.executable_path
                    print(f"     {executable_path}")
                    print(f"     Существует: {os.path.exists(executable_path)}")
                except:
                    print("     Не удалось определить путь")
    except Exception as e:
        print(f"  ❌ Критическая ошибка: {e}")

if __name__ == '__main__':
    check_playwright()
