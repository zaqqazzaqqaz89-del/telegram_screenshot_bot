"""
Сервис для создания скриншотов веб-страниц
С поддержкой разных способов выбора области
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
        selector_type: str = 'full',
        selector: str = None,
        search_text: str = None,
        coordinates: dict = None,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        timeout: int = 30000
    ) -> str:
        """
        Создает скриншот веб-страницы или её части
        
        Args:
            url: URL страницы
            selector_type: Тип выбора области ('full', 'auto', 'text', 'coords', 'css')
            selector: CSS-селектор элемента (для selector_type='css')
            search_text: Текст для поиска элемента (для selector_type='text')
            coordinates: Координаты области (для selector_type='coords')
            viewport_width: Ширина viewport
            viewport_height: Высота viewport
            timeout: Таймаут загрузки страницы
            
        Returns:
            Путь к созданному скриншоту
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        async with async_playwright() as p:
            browser = None
            
            try:
                # Запуск браузера
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
                
                # Попытка с явным путем
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
                        f"Убедитесь что Playwright установлен правильно."
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
                await asyncio.sleep(2)
                
                # Выбираем способ создания скриншота
                if selector_type == 'full':
                    # Вся страница
                    await self._screenshot_full_page(page, filepath)
                
                elif selector_type == 'auto':
                    # Автоопределение главного контента
                    await self._screenshot_auto_content(page, filepath)
                
                elif selector_type == 'text':
                    # Поиск элемента по тексту
                    await self._screenshot_by_text(page, filepath, search_text)
                
                elif selector_type == 'coords':
                    # По координатам
                    await self._screenshot_by_coords(page, filepath, coordinates)
                
                elif selector_type == 'css':
                    # По CSS-селектору
                    await self._screenshot_by_selector(page, filepath, selector)
                
                else:
                    # По умолчанию - вся страница
                    await self._screenshot_full_page(page, filepath)
                
                logger.info(f"Скриншот сохранён: {filepath}")
                return str(filepath)
            
            except Exception as e:
                logger.error(f"Ошибка при создании скриншота: {e}")
                raise
            
            finally:
                await browser.close()
    
    async def _screenshot_full_page(self, page, filepath):
        """Скриншот всей страницы"""
        logger.info("Создание скриншота всей страницы")
        await page.screenshot(path=str(filepath), full_page=True)
    
    async def _screenshot_auto_content(self, page, filepath):
        """Автоопределение главного контента"""
        logger.info("Автоопределение главного контента")
        
        # Список селекторов для основного контента (по приоритету)
        content_selectors = [
            'article',                          # Статьи
            'main',                             # Главный контент
            '[role="main"]',                    # ARIA main
            '.main-content',                    # Популярный класс
            '#main-content',                    # Популярный ID
            '.content',                         # Общий класс контента
            '#content',                         # Общий ID контента
            '.article',                         # Класс статьи
            '.post-content',                    # Контент поста
            '.entry-content',                   # WordPress стандарт
            'div[class*="content"]',            # Любой div с "content"
            'body > div:first-child',           # Первый div в body
        ]
        
        element = None
        for selector in content_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    # Проверяем что элемент видимый и достаточно большой
                    box = await element.bounding_box()
                    if box and box['width'] > 200 and box['height'] > 200:
                        logger.info(f"Найден главный контент: {selector}")
                        break
            except:
                continue
        
        if element:
            await element.screenshot(path=str(filepath))
        else:
            # Если не нашли - делаем скриншот всей страницы
            logger.warning("Главный контент не найден, делаем скриншот всей страницы")
            await self._screenshot_full_page(page, filepath)
    
    async def _screenshot_by_text(self, page, filepath, search_text):
        """Скриншот элемента содержащего указанный текст"""
        logger.info(f"Поиск элемента с текстом: '{search_text}'")
        
        if not search_text:
            raise Exception("Текст для поиска не указан")
        
        try:
            # Пытаемся найти элемент по тексту
            element = await page.locator(f'text={search_text}').first.element_handle()
            
            if not element:
                # Пробуем частичное совпадение
                element = await page.locator(f'text="{search_text}"').first.element_handle()
            
            if element:
                # Находим родительский блок для лучшего контекста
                parent = await element.evaluate_handle('el => el.closest("div, article, section") || el')
                if parent:
                    await parent.as_element().screenshot(path=str(filepath))
                else:
                    await element.screenshot(path=str(filepath))
            else:
                raise Exception(f"Элемент с текстом '{search_text}' не найден")
        
        except PlaywrightTimeout:
            raise Exception(f"Элемент с текстом '{search_text}' не найден или не загрузился")
    
    async def _screenshot_by_coords(self, page, filepath, coordinates):
        """Скриншот области по координатам"""
        if not coordinates:
            raise Exception("Координаты не указаны")
        
        x = coordinates.get('x', 0)
        y = coordinates.get('y', 0)
        width = coordinates.get('width', 800)
        height = coordinates.get('height', 600)
        
        logger.info(f"Создание скриншота области: x={x}, y={y}, {width}x{height}")
        
        await page.screenshot(
            path=str(filepath),
            clip={
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
        )
    
    async def _screenshot_by_selector(self, page, filepath, selector):
        """Скриншот элемента по CSS-селектору"""
        logger.info(f"Создание скриншота элемента: {selector}")
        
        if not selector:
            raise Exception("CSS-селектор не указан")
        
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
