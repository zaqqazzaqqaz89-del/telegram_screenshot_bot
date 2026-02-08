# 🚀 Деплой на Render.com

## Быстрый старт

### 1. Подготовка репозитория

Убедитесь, что все файлы загружены в ваш GitHub репозиторий:

```bash
git add .
git commit -m "Add Telegram Screenshot Bot"
git push origin main
```

### 2. Создание Web Service на Render

1. Зайдите на [dashboard.render.com](https://dashboard.render.com)
2. Нажмите **"New +"** → **"Web Service"**
3. Подключите ваш GitHub репозиторий
4. Выберите репозиторий `telegram_screenshot_bot`

### 3. Настройка сервиса

**Основные настройки:**

- **Name:** `telegram-screenshot-bot` (или любое другое имя)
- **Region:** Выберите ближайший регион
- **Branch:** `main`
- **Root Directory:** (оставьте пустым)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt && playwright install chromium`
- **Start Command:** `python main.py`

**Instance Type:**
- Выберите **Free** или **Starter** (рекомендуется Starter для стабильной работы)

### 4. Environment Variables (Переменные окружения)

Добавьте в разделе **Environment**:

```
TELEGRAM_TOKEN=ваш_токен_от_BotFather
```

**Опционально:**
```
SCREENSHOTS_DIR=screenshots
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080
PAGE_TIMEOUT=30000
```

### 5. Дополнительные настройки

**В разделе "Advanced":**

- **Auto-Deploy:** Включите (Yes) для автоматического деплоя при push в GitHub
- **Health Check Path:** (оставьте пустым для background worker)

### 6. Деплой

Нажмите **"Create Web Service"** и дождитесь завершения деплоя.

---

## ⚠️ Важные замечания

### Python версия

Файл `runtime.txt` указывает на Python 3.12:
```
python-3.12
```

Если Render все равно использует Python 3.13, обе версии совместимы (greenlet 3.1.1+ работает с Python 3.13).

### Playwright браузер

Build команда устанавливает браузер Chromium:
```bash
playwright install chromium
```

Если возникают проблемы с зависимостями браузера, используйте:
```bash
pip install -r requirements.txt && playwright install chromium && playwright install-deps
```

### Free план vs Starter

**Free план:**
- ✅ Работает для тестирования
- ⚠️ Засыпает после 15 минут неактивности
- ⚠️ Имеет ограничения по CPU/памяти

**Starter план ($7/месяц):**
- ✅ Работает 24/7 без перерыва
- ✅ Больше ресурсов
- ✅ Подходит для продакшена

---

## 🔧 Устранение проблем

### "RuntimeError: no running event loop"

**Исправлено!** Версия main.py в этом репозитории уже содержит исправление. Если используете старую версию:

```python
# В методе run(), переместите scheduler.start() внутрь post_init
async def post_init(application):
    self.scheduler.start()
    logger.info("Планировщик запущен")

application.post_init = post_init
```

### "Failed building wheel for greenlet"

**Решение 1:** Обновите versions в requirements.txt:
```
APScheduler==3.11.0
greenlet>=3.1.1
```

**Решение 2:** Используйте `main_simple.py` вместо `main.py`:
```bash
# В Start Command укажите:
python main_simple.py
```

### Playwright не запускается

Добавьте в Build Command:
```bash
pip install -r requirements.txt && playwright install chromium && playwright install-deps
```

### Бот не отвечает

1. Проверьте логи в Render Dashboard → Logs
2. Убедитесь что `TELEGRAM_TOKEN` правильный
3. Проверьте что сервис запущен (не в статусе "suspended")

---

## 📊 Мониторинг

### Просмотр логов

В Render Dashboard:
1. Откройте ваш сервис
2. Перейдите в раздел **"Logs"**
3. Вы увидите:
   ```
   INFO - Бот запущен
   INFO - Планировщик запущен
   ```

### Проверка работы

Отправьте боту в Telegram:
```
/start
```

Если бот отвечает - деплой успешен! 🎉

---

## 🔄 Обновление кода

При обновлении кода в GitHub:

1. Сделайте изменения локально
2. Закоммитьте и запушьте:
   ```bash
   git add .
   git commit -m "Update bot"
   git push origin main
   ```
3. Render автоматически задеплоит новую версию (если включен Auto-Deploy)

---

## 💡 Альтернативные команды запуска

### Для упрощенной версии (без APScheduler)
```bash
# Start Command:
python main_simple.py
```

### С подробным логированием
```bash
# Start Command:
python -u main.py
```

---

## 📝 Структура для Render

Убедитесь что в репозитории есть:

```
telegram_screenshot_bot/
├── main.py                    # ✅ Обязательно
├── screenshot_service.py      # ✅ Обязательно
├── config.py                  # ✅ Обязательно
├── requirements.txt           # ✅ Обязательно
├── runtime.txt               # ✅ Рекомендуется
├── .env.example              # ℹ️ Для справки (не используется на Render)
└── README.md                 # ℹ️ Документация
```

**Важно:** Файл `.env` НЕ нужен на Render - используйте Environment Variables в настройках сервиса!

---

## 🎯 Checklist перед деплоем

- [ ] Все файлы загружены в GitHub
- [ ] `runtime.txt` присутствует
- [ ] `requirements.txt` актуален
- [ ] Получен TELEGRAM_TOKEN от @BotFather
- [ ] TELEGRAM_TOKEN добавлен в Environment Variables на Render
- [ ] Build Command настроен: `pip install -r requirements.txt && playwright install chromium`
- [ ] Start Command настроен: `python main.py`
- [ ] Выбран Instance Type (Free или Starter)

---

**После успешного деплоя бот будет работать 24/7 и автоматически отправлять скриншоты по расписанию!** 🚀
