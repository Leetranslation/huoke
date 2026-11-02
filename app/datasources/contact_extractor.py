"""联系人提取器：爬公司官网联系页，提取邮箱与联系人（异步）。

优先用 DeepSeek Fetch API（无反爬、返回 Markdown），失败回退 httpx。
"""

import re
from dataclasses import dataclass

import httpx

from app.datasources.deepseek_fetcher import DeepSeekFetcher

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

CONTACT_PATHS = [
    "/",
    "/contact",
    "/contacts",
    "/contact-us",
    "/about",
    "/kontakt",
    "/impressum",
    "/contatti",
    "/contacto",
]

EXCLUDE = (
    "noreply",
    "no-reply",
    "example.",
    "sentry",
    "your-email",
    "yourname",
    "@2x",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".gif",
)


@dataclass
class ContactRaw:
    email: str
    name: str = ""
    title: str = ""


class ContactExtractor:
    """从公司官网提取邮箱（首页优先，最多尝试 3 个页面）。"""

    def __init__(self, timeout: float = 8.0, use_deepseek: bool = True):
        self._fetcher = DeepSeekFetcher() if use_deepseek else None
        self._timeout = timeout

    def close(self) -> None:
        """兼容旧调用（异步版无长连接需关闭）。"""

    async def extract(self, website: str, max_emails: int = 3) -> list[ContactRaw]:
        """从官网提取邮箱；website 为空或失败返回空列表。"""
        if not website or not website.startswith("http"):
            return []

        base = website.rstrip("/")
        found: dict[str, ContactRaw] = {}
        attempts = 0

        for path in CONTACT_PATHS:
            if len(found) >= max_emails or attempts >= 3:
                break
            attempts += 1
            text = await self._get_text(base + path)
            if not text:
                continue
            for email in self._find_emails(text):
                if email.lower() not in {k.lower() for k in found}:
                    found[email] = ContactRaw(email=email)

        return list(found.values())

    async def _get_text(self, url: str) -> str:
        """优先 DeepSeek Fetch，失败回退 httpx。"""
        if self._fetcher:
            text = await self._fetcher.fetch(url)
            if text:
                return text
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": UA},
            ) as client:
                r = await client.get(url)
            if r.status_code == 200:
                return r.text or ""
        except Exception:  # noqa: BLE001
            pass
        return ""

    @staticmethod
    def _find_emails(html: str) -> list[str]:
        """从 HTML/Markdown 提取邮箱并过滤垃圾。"""
        result = []
        for email in EMAIL_RE.findall(html or ""):
            low = email.lower()
            if any(x in low for x in EXCLUDE):
                continue
            if len(email) > 100:
                continue
            if email not in result:
                result.append(email)
        return result[:5]
