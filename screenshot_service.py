"""
Сервис для создания скриншотов веб-страниц
"""
import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


class ScreenshotService:
    def __init__(self, screenshots_dir: str = "screenshots"):
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def take_screenshot(
        self,
        url: str,
        selector: str = None,
        full_page: bool = True,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        timeout: int = 30000
    ) -> str:
        """
        Создает скриншот веб-страницы или её части
        
        Args:
            url: URL страницы
            selector: CSS-селектор элемента (если None, скриншот всей страницы)
            full_page: Скриншот всей страницы (если selector=None)
            viewport_width: Ширина viewport
            viewport_height: Высота viewport
            timeout: Таймаут загрузки страницы в миллисекундах
            
        Returns:
            Путь к созданному скриншоту
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        async with async_playwright() as p:
            # Пробуем разные способы запуска браузера
            browser = None
            
            try:
                # Попытка 1: Стандартный запуск
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu',
                        '--single-process',
                        '--no-zygote'
                    ]
                )
            except Exception as e:
                logger.warning(f"Стандартный запуск не удался: {e}")
                
                # Попытка 2: С явным указанием пути к браузеру
                try:
                    browser_path = '/opt/render/.cache/ms-playwright/chromium-1148/chrome-linux/chrome'
                    if os.path.exists(browser_path):
                        browser = await p.chromium.launch(
                            headless=True,
                            executable_path=browser_path,
                            args=[
                                '--no-sandbox',
                                '--disable-setuid-sandbox',
                                '--disable-dev-shm-usage',
                                '--disable-accelerated-2d-canvas',
                                '--disable-gpu',
                                '--single-process',
                                '--no-zygote'
                            ]
                        )
                except Exception as e2:
                    logger.error(f"Запуск с явным путем не удался: {e2}")
                    raise Exception(
                        f"Не удалось запустить браузер.\n"
                        f"Убедитесь что Playwright установлен правильно:\n"
                        f"pip install playwright && playwright install chromium"
                    )
            
            if not browser:
                raise Exception("Браузер не был запущен")
            
            try:
                context = await browser.new_context(
                    viewport={'width': viewport_width, 'height': viewport_height},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                page = await context.new_page()
                
                # Переходим на страницу
                logger.info(f"Загрузка страницы: {url}")
                await page.goto(url, wait_until='networkidle', timeout=timeout)
                
                # Небольшая задержка для полной загрузки
                await asyncio.sleep(2)
                
                # Делаем скриншот
                if selector:
                    logger.info(f"Создание скриншота элемента: {selector}")
                    try:
                        element = await page.wait_for_selector(
                            selector,
                            timeout=10000,
                            state='visible'
                        )
                        
                        if element:
                            await element.screenshot(path=str(filepath))
                        else:
                            raise Exception(f"Элемент '{selector}' не найден на странице")
                    
                    except PlaywrightTimeout:
                        raise Exception(
                            f"Элемент '{selector}' не найден или не загрузился.\n"
                            "Проверьте правильность селектора."
                        )
                else:
                    logger.info("Создание скриншота всей страницы")
                    await page.screenshot(
                        path=str(filepath),
                        full_page=full_page
                    )
                
                logger.info(f"Скриншот сохранён: {filepath}")
                return str(filepath)
            
            except Exception as e:
                logger.error(f"Ошибка при создании скриншота: {e}")
                raise
            
            finally:
                await browser.close()
