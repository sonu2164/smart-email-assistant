import nest_asyncio
nest_asyncio.apply()

from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langchain_community.tools.playwright.click import ClickTool

import asyncio

async def _init_click_tool():
    # 1) launch a shared async playwright browser context
    browser = await create_async_playwright_browser()
    # 2) wrap and return the ClickTool
    return ClickTool(async_browser=browser)

# synchronous handle we can import elsewhere
click_tool: ClickTool = asyncio.get_event_loop().run_until_complete(_init_click_tool())