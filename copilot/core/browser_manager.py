"""
浏览器会话管理 - 复用 CNKI skill 的 ChromeSession
封装 CDP 连接、页面管理、反爬处理
"""
import sys
import os
import asyncio

CNKI_SKILL_DIR = os.environ.get("CNKI_SKILL_DIR", "")
if not CNKI_SKILL_DIR:
    candidates = [
        os.path.join(os.path.expanduser("~"), ".codex", "skills", "_shared", "cnki"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared", "cnki"),
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "browser.py")):
            CNKI_SKILL_DIR = c
            break

if CNKI_SKILL_DIR and CNKI_SKILL_DIR not in sys.path:
    sys.path.insert(0, CNKI_SKILL_DIR)

from browser import ChromeSession, CnkiError
from cnki_selectors import ADVANCED_SEARCH_URL, SEARCH_URL

DEFAULT_CDP_URL = "http://127.0.0.1:9222"


class BrowserManager:
    """管理 Chrome CDP 浏览器会话"""

    def __init__(self, cdp_url: str = DEFAULT_CDP_URL):
        self.cdp_url = cdp_url
        self.session = None

    async def connect(self):
        self.session = ChromeSession(self.cdp_url)
        await self.session.__aenter__()
        return self

    async def close(self):
        if self.session:
            await self.session.__aexit__(None, None, None)

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, *args):
        await self.close()

    async def new_page(self):
        return await self.session.context.new_page()

    async def safe_delay(self, min_s=1.0, max_s=2.5):
        import random
        await asyncio.sleep(random.uniform(min_s, max_s))

    async def check_captcha(self, page):
        """检测并等待用户处理验证码"""
        try:
            await self.session.require_no_captcha(page)
        except CnkiError as e:
            if e.code == "captcha":
                print("\n  [!!!] 知网弹出验证码，请在Chrome中手动完成，完成后按回车继续...")
                input()
                await self.session.require_no_captcha(page)
            else:
                raise
