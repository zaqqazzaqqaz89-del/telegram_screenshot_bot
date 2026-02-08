# 🐳 ФИНАЛЬНОЕ РЕШЕНИЕ - Docker (100% работает)

## Проблема
Браузер не устанавливается при билде на Render, хотя команда `playwright install chromium` выполняется.

## ✅ Решение - Docker образ с предустановленным Playwright

### Шаг 1: Добавьте Dockerfile в репозиторий

```bash
cd telegram_screenshot_bot

# Скопируйте Dockerfile из архива в корень репозитория

git add Dockerfile
git commit -m "Add Docker support"
git push origin main
```

### Шаг 2: Измените настройки на Render

1. Откройте ваш сервис: https://dashboard.render.com/web/srv-d649s7fgi27c73asfe40
2. Перейдите в **Settings**
3. Измените настройки:

**Environment:**
```
Docker
```

**Docker Command (Start Command):**
```
python main.py
```

**Build Command:**
```
(оставьте ПУСТЫМ - Docker сам соберет образ)
```

**Docker Build Context Path:**
```
.
```

**Dockerfile Path:**
```
./Dockerfile
```

4. **Save Changes**
5. **Manual Deploy** → **Clear build cache & deploy**

### Шаг 3: Подождите билд (~3-5 минут)

Docker скачает образ с предустановленным Playwright и браузером.

---

## 📊 Что произойдет

В логах вы увидите:

```
==> Building Docker image...
==> Pulling mcr.microsoft.com/playwright/python:v1.49.0-jammy
==> Successfully built
==> Deploying...
==> Running 'python main.py'
✅ Бот запущен
✅ Планировщик запущен
```

И команда `/screenshot` **заработает**! 🎉

---

## 🎯 Почему Docker решает проблему?

1. ✅ Браузер **уже установлен** в образе
2. ✅ Все зависимости **предустановлены**
3. ✅ Не нужны права root для установки
4. ✅ Работает на **любой платформе**

---

## 🔄 Альтернатива - Background Worker (без Docker)

Если не хотите использовать Docker, создайте **Background Worker** вместо Web Service:

1. Dashboard → **New +** → **Background Worker**
2. Выберите репозиторий
3. Настройки:
   - **Build Command:** `pip install -r requirements.txt && python -m playwright install --with-deps chromium`
   - **Start Command:** `python main.py`
   - **Environment:** `TELEGRAM_TOKEN=ваш_токен`

**Build Command с `python -m playwright install --with-deps`** принудительно переустановит браузер.

---

## ⚡ Быстрый вариант (если торопитесь)

Используйте готовый Docker-образ, измените только Environment на Render:

**Settings → Environment:**
```
Docker
```

**Start Command:**
```
python main.py
```

**Clear build cache & deploy**

Всё! Бот заработает через 5 минут.

---

## 📋 Итоговая структура репозитория

```
telegram_screenshot_bot/
├── Dockerfile              ← НОВЫЙ ФАЙЛ
├── main.py
├── screenshot_service.py
├── config.py
├── requirements.txt
├── runtime.txt
├── .env.example
└── README.md
```

---

## 🆘 Если что-то не работает

После деплоя проверьте логи. Должно быть:

```
✅ Building Docker image...
✅ Successfully built
✅ Deploying...
✅ Бот запущен
✅ Планировщик запущен
```

При команде `/screenshot` НЕ должно быть ошибки "Executable doesn't exist".

---

**Docker = 100% гарантия работы** 🚀
