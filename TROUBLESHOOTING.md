# 🔧 Быстрое решение проблем

## Проблема 1: "RuntimeError: no running event loop"

Эта ошибка возникает при деплое на Render (и других платформах) когда APScheduler пытается запуститься до создания event loop.

```
RuntimeError: no running event loop
File ".../apscheduler/schedulers/asyncio.py", line 35, in start
    self._eventloop = asyncio.get_running_loop()
```

### ✅ РЕШЕНИЕ

**Версия main.py в этом репозитории уже исправлена!** Просто используйте её.

Если проблема все еще возникает, убедитесь что используете последнюю версию main.py из этого репозитория.

**Или используйте альтернативную версию:**
```bash
# В настройках Render измените Start Command на:
python main_simple.py
```

---

## Проблема 2: "Failed building wheel for greenlet"

Эта ошибка возникает при использовании Python 3.13+, так как пакет `greenlet` (зависимость APScheduler) пока не полностью совместим с этой версией.

---

## ✅ РЕШЕНИЕ 1: Упрощенная версия (для Python 3.13+)

Используйте версию бота без APScheduler. Она работает точно так же, но использует встроенный asyncio для планирования.

### Шаги:

```bash
# 1. Переключитесь на упрощенную версию
cp main_simple.py main.py
cp requirements_simple.txt requirements.txt

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Установите браузер Playwright
playwright install chromium

# 4. Настройте .env файл
cp .env.example .env
nano .env  # добавьте ваш TELEGRAM_TOKEN

# 5. Запустите бота
python main.py
```

**Разница:** Упрощенная версия использует asyncio вместо APScheduler. Функционально работает идентично.

---

## ✅ РЕШЕНИЕ 2: Использовать Python 3.12

Если вы хотите использовать стандартную версию с APScheduler:

### Вариант A: Через pyenv

```bash
# Установите pyenv (если еще не установлен)
curl https://pyenv.run | bash

# Установите Python 3.12
pyenv install 3.12.8
pyenv local 3.12.8

# Проверьте версию
python --version  # Должно показать Python 3.12.8

# Установите зависимости
pip install -r requirements.txt
playwright install chromium

# Запустите бота
python main.py
```

### Вариант B: Через виртуальное окружение

```bash
# Если у вас установлен Python 3.12
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
playwright install chromium
python main.py
```

---

## ✅ РЕШЕНИЕ 3: Деплой на облачные платформы

### Render.com

Файл `runtime.txt` уже настроен:
```
python-3.12.8
```

Render автоматически использует эту версию. Просто загрузите проект.

### Heroku

```bash
# Создайте файл runtime.txt (уже создан)
echo "python-3.12.8" > runtime.txt

# Деплой
git add .
git commit -m "Add runtime"
git push heroku main
```

### Railway / Vercel

Добавьте в настройки проекта:
```
PYTHON_VERSION=3.12.8
```

---

## 📊 Сравнение версий

| Аспект | main.py (APScheduler) | main_simple.py (asyncio) |
|--------|----------------------|--------------------------|
| Python | 3.11-3.12 | 3.11+ (включая 3.13) |
| Планировщик | APScheduler (внешняя библиотека) | asyncio (встроенный) |
| Точность | Миллисекунды | Секунды |
| Зависимости | 4 пакета | 3 пакета |
| Производительность | Немного выше | Отличная |
| Стабильность | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Вывод:** Обе версии полностью функциональны. Выбирайте по версии Python.

---

## 🧪 Как проверить, что все работает

```bash
# 1. Проверьте версию Python
python --version

# 2. Запустите бота
python main.py

# 3. Вы должны увидеть:
# INFO - Бот запущен
# или
# INFO - Бот запущен (версия без APScheduler)
```

---

## 🆘 Все еще не работает?

1. **Проверьте логи:** Посмотрите на полный вывод ошибки
2. **Проверьте .env:** Убедитесь, что TELEGRAM_TOKEN правильный
3. **Проверьте Playwright:**
   ```bash
   playwright install chromium
   playwright install-deps  # Linux
   ```
4. **Создайте issue:** Отправьте полный лог ошибки

---

## 💡 Рекомендации

- **Python 3.13+** → используйте `main_simple.py`
- **Python 3.12** → используйте `main.py` (по умолчанию)
- **Деплой** → файл `runtime.txt` автоматически установит Python 3.12.8
- **Локально** → любая версия Python 3.11+ с соответствующими файлами

---

**После применения любого решения бот будет работать полностью!** 🎉
