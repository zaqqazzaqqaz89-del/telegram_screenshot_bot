# 🔧 Решение БЕЗ Docker - Принудительная переустановка браузера

## Проблема
Команда `playwright install chromium` выполняется, но браузер не скачивается (используется старый кеш).

## ✅ Решение - Форсировать переустановку

### Вариант 1: Измените Build Command на Render

**Settings → Build Command:**
```bash
pip install -r requirements.txt && python -m playwright install --force chromium
```

Флаг `--force` принудительно переустановит браузер, игнорируя кеш.

**Или более надежный вариант:**
```bash
pip install -r requirements.txt && rm -rf /opt/render/.cache/ms-playwright && python -m playwright install chromium
```

Это удалит старый кеш и установит браузер заново.

**Save Changes** → **Clear build cache & deploy**

---

### Вариант 2: Добавьте Environment Variable

**Settings → Environment → Add Environment Variable:**

```
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
```

Это гарантирует что браузер будет скачан в правильную директорию.

**Save Changes** → **Manual Deploy**

---

### Вариант 3: Создайте Background Worker (РЕКОМЕНДУЮ)

Background Worker лучше подходит для ботов:

1. **Render Dashboard** → **New +** → **Background Worker**
2. Выберите репозиторий `telegram_screenshot_bot`
3. Настройки:

**Build Command:**
```bash
pip install -r requirements.txt && playwright install chromium
```

**Start Command:**
```bash
python main.py
```

**Environment Variables:**
```
TELEGRAM_TOKEN=ваш_токен
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
```

4. **Create Background Worker**

**Плюсы Background Worker:**
- ✅ Не проверяет порты (нет "No open ports detected")
- ✅ Более стабильная работа
- ✅ Правильный тип сервиса для ботов

---

## 🎯 Какой вариант выбрать?

| Вариант | Сложность | Надежность | Рекомендация |
|---------|-----------|------------|--------------|
| Docker | Средняя | ⭐⭐⭐⭐⭐ | ✅ Лучший вариант |
| Background Worker | Низкая | ⭐⭐⭐⭐ | ✅ Хороший вариант |
| Build Command с --force | Низкая | ⭐⭐⭐ | ⚠️ Может сработать |

---

## 📋 Проверка после деплоя

В логах должно быть:

```
==> Running build command ...
Successfully installed ...
Downloading Chromium 131.0.6778.33 ...  ← ВАЖНО!
|████████████████████████████████| 100% of 161.3 MiB
Chromium downloaded to /opt/render/.cache/ms-playwright/chromium-1148
==> Build successful 🎉
==> Running 'python main.py'
Бот запущен
Планировщик запущен
```

**Ключевой момент:** Должна быть строка **"Downloading Chromium"**!

Если её нет - браузер не скачивается. Используйте Docker (см. DOCKER_SOLUTION.md).

---

## 🆘 Если проблема осталась

Попробуйте в таком порядке:

1. ✅ **Background Worker** с `PLAYWRIGHT_BROWSERS_PATH` 
2. ✅ **Docker** (100% работает)
3. ⚠️ Build Command с `--force`

**Самый надежный:** Docker решение (см. DOCKER_SOLUTION.md)

---

**После любого из этих решений бот должен заработать!** 🚀
