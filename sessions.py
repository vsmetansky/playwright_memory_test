import logging
from asyncio import wait_for
from uuid import uuid4

from playwright import async_playwright

logger = logging.getLogger(__name__)


class BrowserSession:
    def __init__(self):
        self.id = str(uuid4())
        self.playwright = None
        self.browser = None
        self.context = None

    async def open(self):
        self.playwright = await async_playwright().start()
        logger.debug(f'[{self.id}] playwright started')
        self.browser = await wait_for(self.playwright.chromium.launch(slowMo=10), timeout=40)
        logger.debug(f'[{self.id}] browser created')
        self.context = await self.browser.newContext()

    async def close(self):
        logger.debug(f'[{self.id}] closing session')
        try:
            await self.browser.close()
        except Exception:
            try:
                await self.context.close()
            except Exception:
                pass
        finally:
            await self.playwright.stop()
