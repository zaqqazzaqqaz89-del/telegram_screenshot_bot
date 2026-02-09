# 🚀 Telegram Screenshot Bot - Полная инструкция

Telegram бот для автоматического создания скриншотов веб-сайтов.

## 📋 Что умеет бот

- ✅ Создание скриншотов полной страницы или выбранной области (через CSS-селекторы)
- ✅ Автоматическая отправка скриншотов по расписанию
- ✅ Работа в режиме WEBHOOK на Render Web Service
- ✅ Поддержка Docker для стабильной работы браузера

---

## 🎯 БЫСТРЫЙ СТАРТ (3 шага)

### Шаг 1: Создать Telegram бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям (придумайте имя и username для бота)
4. **Скопируйте токен** (формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Шаг 2: Загрузить код в GitHub

```bash
# Создайте новый репозиторий на GitHub
# Клонируйте к себе
git clone https://github.com/ваш-username/telegram_screenshot_bot
cd telegram_screenshot_bot

# Скопируйте все файлы из этой папки в репозиторий
# Затем:
git add .
git commit -m "Initial commit"
git push origin main
```

### Шаг 3: Развернуть на Render

#### Вариант A: Web Service + Webhook (рекомендуется)

1. Зайдите на [render.com](https://render.com)
2. **New +** → **Web Service**
3. Подключите ваш GitHub репозиторий
4. Настройки:

```
Name: telegram-screenshot-bot (любое имя)
Region: выберите ближайший
Branch: main
Root Directory: (пусто)
Runtime: Python 3
Build Command: pip install -r requirements.txt && playwright install chromium
Start Command: python main.py
Instance Type: Free или Starter
```

5. **Environment Variables:**

```
TELEGRAM_TOKEN = ваш_токен_от_BotFather
```

6. **Create Web Service**
7. Подождите 3-5 минут

✅ **Готово!** Бот работает!

#### Вариант B: Docker (если браузер не работает)

1. Повторите шаги 1-3 из Варианта A
2. В настройках выберите:

```
Environment: Docker
Docker Build Context Path: .
Dockerfile Path: ./Dockerfile
Start Command: python main.py
```

3. **Create Web Service**

✅ **Готово!** Браузер работает на 100%!

---

## 📖 Использование бота

### В Telegram найдите вашего бота и отправьте:

```
/start
```

### Основные команды:

```
/seturl https://example.com     - Установить URL сайта
/setselector .main-content      - Выбрать область (опционально)
/screenshot                     - Сделать скриншот сейчас
/schedule                       - Настроить автоматическую отправку
/settings                       - Показать настройки
/help                           - Справка
```

### Примеры:

**Скриншот всей страницы:**
```
/seturl https://news.ycombinator.com
/screenshot
```

**Скриншот конкретной области:**
```
/seturl https://github.com
/setselector .dashboard-sidebar
/screenshot
```

**Ежедневные скриншоты:**
```
/seturl https://weather.com
/schedule
→ Включить → Изменить время → 09:00
```

---

## 🔍 Как найти CSS-селектор

1. Откройте сайт в браузере
2. Нажмите **F12** (откроется DevTools)
3. Нажмите иконку **"выбрать элемент"** (стрелка в углу)
4. Кликните на нужный элемент на странице
5. В DevTools посмотрите:
   - `class="..."` → используйте `.class-name`
   - `id="..."` → используйте `#element-id`

**Или:**
- ПКМ на элементе в DevTools → **Copy** → **Copy selector**

---

## ⚙️ Настройка расписания

Время указывается в **UTC**. Для Москвы (UTC+3):

| Время МСК | Время UTC | Использование |
|-----------|-----------|---------------|
| 09:00 | 06:00 | Утренние новости |
| 12:00 | 09:00 | Дневные данные |
| 18:00 | 15:00 | Вечерние обновления |
| 21:00 | 18:00 | Итоги дня |

---

## 🐳 Docker вариант (100% работает)

Если скриншоты не создаются (ошибка браузера), используйте Docker:

### На Render:

1. **Settings** → **Environment**: выберите **Docker**
2. **Start Command**: `python main.py`
3. **Save Changes** → **Manual Deploy** → **Clear build cache & deploy**

Браузер будет предустановлен в Docker образе!

---

## 🛠 Локальная разработка

### Установка:

```bash
# Клонируйте репозиторий
git clone your-repo-url
cd telegram_screenshot_bot

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt
playwright install chromium

# Создайте .env файл
cp .env.example .env
# Отредактируйте .env и добавьте TELEGRAM_TOKEN
```

### Запуск локально (polling режим):

Для локальной разработки используйте polling вместо webhook.

Создайте `main_local.py`:

```python
# В конце файла замените:
# application.run_webhook(...)

# На:
application.run_polling(allowed_updates=Update.ALL_TYPES)
```

Запуск:
```bash
python main_local.py
```

---

## 📊 Структура проекта

```
telegram_screenshot_bot/
├── main.py                  # Основной файл бота (WEBHOOK версия)
├── screenshot_service.py    # Сервис создания скриншотов
├── config.py               # Конфигурация
├── requirements.txt        # Зависимости (с [webhooks])
├── Dockerfile              # Docker образ
├── .env.example           # Пример конфигурации
├── .gitignore            # Git ignore
├── screenshots/          # Временные скриншоты (создается автоматически)
└── README.md            # Этот файл
```

---

## ❓ Частые вопросы

### Бот не отвечает

**Проверьте:**
1. Правильный ли TELEGRAM_TOKEN в Environment Variables на Render
2. Запущен ли сервис (зеленый статус на Render)
3. Есть ли ошибки в логах

### Ошибка "Executable doesn't exist"

**Решение:** Используйте Docker вариант:
- Settings → Environment: **Docker**
- Clear build cache & deploy

### Ошибка "Port scan timeout"

**Решение:** Убедитесь что используете:
- `python-telegram-bot[webhooks]` в requirements.txt
- `application.run_webhook(...)` в main.py (БЕЗ asyncio.run)

### Бот медленно создает скриншоты

**Нормально!** Первый скриншот всегда дольше (запуск браузера).
Следующие будут быстрее.

---

## 🔄 Обновление

```bash
# Внесите изменения в код
git add .
git commit -m "Update bot"
git push origin main

# Render автоматически задеплоит новую версию
```

---

## 🆘 Поддержка

**Логи на Render:**
- Откройте ваш сервис → **Logs**
- Ищите строки с ERROR или WARNING

**Проверка webhook:**
```
https://ваш-сервис.onrender.com/webhook
```
Должно показать: `405 Method Not Allowed` (это нормально!)

---

## 📝 Лицензия

Проект создан для образовательных целей. Используйте на свой риск.

---

## 🎉 Готово!

**Ваш бот работает 24/7 и автоматически создает скриншоты!**

Если возникли проблемы - проверьте логи на Render и следуйте разделу "Частые вопросы".
