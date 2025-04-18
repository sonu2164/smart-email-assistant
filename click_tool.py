import asyncio
from typing import Optional, Type
from langchain.tools import BaseTool
from langchain.pydantic_v1 import Field

class ClickTool(BaseTool):
    name: str = Field(default="click_tool", description="Tool for clicking unsubscribe links.")
    description: str = "Navigate to a URL and click on unsubscribe buttons."

    def _create_event_loop(self):
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    async def _navigate_and_click(self, url: str, button_text: Optional[str] = None):
        from playwright.async_api import async_playwright
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=10000)

            if button_text:
                selectors = [
                    f"button:has-text('{button_text}')",
                    f"a:has-text('{button_text}')",
                    f"input[value='{button_text}']",
                    f"[role='button']:has-text('{button_text}')",
                    f"*:has-text('{button_text}')"
                ]
                for selector in selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            await element.click()
                            await page.wait_for_load_state("networkidle", timeout=10000)
                            await page.close()
                            await browser.close()
                            await p.stop()
                            return f"Successfully clicked button with text '{button_text}' on {url}"
                    except:
                        continue

            await page.close()
            await browser.close()
            await p.stop()
            return f"Visited {url} but no button clicked."
        except Exception as e:
            await page.close()
            await browser.close()
            await p.stop()
            return f"Error on {url}: {str(e)}"

    def _run(self, url: str, button_text: Optional[str] = None) -> str:
        loop = self._create_event_loop()
        return loop.run_until_complete(self._navigate_and_click(url, button_text))

    def _call(self, **kwargs) -> str:
        return self._run(kwargs["url"], kwargs.get("button_text", None))

    args_schema: Optional[Type] = None  # No schema for now, could be defined with Pydantic if needed
