"""联系人提取器：爬公司官网联系页，提取邮箱与联系人（异步）。

优先用 DeepSeek Fetch API（无反爬、返回 Markdown），失败回退 httpx。
"""

import asyncio
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

    def __init__(self, timeout: float = 6.0, use_deepseek: bool = False):
        # DeepSeekFetch 单次要 17 秒，命中率还低；默认用 httpx，拿不到交给搜索引擎兜底
        self._fetcher = DeepSeekFetcher() if use_deepseek else None
        self._timeout = timeout

    def close(self) -> None:
        """兼容旧调用（异步版无长连接需关闭）。"""

    async def extract(self, website: str, max_emails: int = 3) -> list[ContactRaw]:
        """从官网提取邮箱；website 为空或失败返回空列表。

        3 个候选页面并发抓取（原来串行，每家要等 3 次 Fetch API）。
        """
        if not website or not website.startswith("http"):
            return []

        base = website.rstrip("/")
        # 只抓最可能出邮箱的 2 个页面，并发
        urls = [base + p for p in CONTACT_PATHS[:2]]
        texts = await asyncio.gather(
            *[self._get_text(u) for u in urls], return_exceptions=True
        )

        found: dict[str, ContactRaw] = {}
        for text in texts:
            if not isinstance(text, str) or not text:
                continue
            for email in self._find_emails(text):
                if len(found) >= max_emails:
                    break
                found.setdefault(email.lower(), ContactRaw(email=email))
            if len(found) >= max_emails:
                break

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
