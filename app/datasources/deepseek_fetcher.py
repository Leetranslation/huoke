"""DeepSeek Fetch API：抓网页返回 Markdown（异步，0.005 元/次，仅成功计费）。"""

import re

import httpx

from app.core.config import settings

FETCH_URL = "https://api.deepseek.com/v1/tools/fetch"


class DeepSeekFetcher:
    """抓取单个网页，返回清理后的 Markdown 正文；失败返回空串。"""

    async def fetch(self, url: str) -> str:
        if not url or not url.startswith("http"):
            return ""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    FETCH_URL,
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"url": url},
                )
            if r.status_code != 200:
                return ""
            content = r.json().get("content", "") or ""
            return self._clean(content)
        except Exception:  # noqa: BLE001
            return ""

    @staticmethod
    def _clean(text: str) -> str:
        """去掉 Markdown 转义反斜杠。"""
        text = re.sub(r"\\([#\-'. ,()\[\]!*_`>|])", r"\1", text)
        return text.strip()
