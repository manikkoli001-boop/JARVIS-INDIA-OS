import asyncio
from playwright.async_api import async_playwright, TimeoutError


class BrowserController:
    """
    Async Playwright browser controller with safe cleanup.
    Production-ready implementation for browser automation.
    """

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def open_url(self, url: str) -> None:
        if not self.playwright:
            try:
                self.playwright = await async_playwright().start()
            except Exception as e:
                print(f"Error starting Playwright: {e}")
                return
        if not self.browser:
            try:
                self.browser = await self.playwright.chromium.launch()
            except Exception as e:
                print(f"Error launching browser: {e}")
                return
        if not self.context:
            try:
                self.context = await self.browser.new_context()
            except Exception as e:
                print(f"Error creating new context: {e}")
                return
        if not self.page:
            try:
                self.page = await self.context.new_page()
            except Exception as e:
                print(f"Error creating new page: {e}")
                return
        try:
            await self.page.goto(url)
        except TimeoutError:
            print("Page load timed out")
        except Exception as e:
            print(f"Error navigating to URL: {e}")

    async def search_google(self, query: str) -> None:
        await self.open_url("https://www.google.com")
        try:
            await self.page.fill('textarea[name="q"]', query)
            await self.page.press('textarea[name="q"]', 'Enter')
            await asyncio.sleep(2)  # Wait for search results to load
        except Exception as e:
            print(f"Error searching Google: {e}")

    async def get_page_text(self) -> str:
        try:
            return await self.page.inner_text('body')
        except Exception as e:
            print(f"Error getting page text: {e}")
            return ""

    async def click_text(self, text: str) -> None:
        try:
            await self.page.click(f'text={text}')
        except Exception as e:
            print(f"Error clicking text: {e}")

    async def type_text(self, selector: str, text: str) -> None:
        try:
            await self.page.fill(selector, text)
        except Exception as e:
            print(f"Error typing text: {e}")

    async def get_links(self) -> list:
        try:
            return await self.page.eval_on_selector_all('a', 'elements => elements.map(e => e.href)')
        except Exception as e:
            print(f"Error getting links: {e}")
            return []

    async def open_new_tab(self, url: str) -> None:
        try:
            new_page = await self.context.new_page()
            await new_page.goto(url)
            self.page = new_page
        except Exception as e:
            print(f"Error opening new tab: {e}")

    async def close_tab(self) -> None:
        try:
            await self.page.close()
            self.page = None
        except Exception as e:
            print(f"Error closing tab: {e}")

    async def scroll_down(self) -> None:
        try:
            await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
        except Exception as e:
            print(f"Error scrolling down: {e}")

    async def wait_for_text(self, text: str) -> None:
        try:
            await self.page.wait_for_selector(f'text={text}')
        except Exception as e:
            print(f"Error waiting for text: {e}")

    async def screenshot(self, path: str) -> None:
        try:
            await self.page.screenshot(path=path, full_page=True)
        except Exception as e:
            print(f"Error taking screenshot: {e}")

    async def close_browser(self) -> None:
        if self.page:
            await self.page.close()
            self.page = None
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_browser()
