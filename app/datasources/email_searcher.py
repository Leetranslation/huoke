"""邮箱搜索器：用 DeepSeek Search API 搜公司邮箱（异步，0.005 元/次）。"""

import re

import httpx

from app.core.config import settings

SEARCH_URL = "https://api.deepseek.com/v1/tools/search"

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

EXCLUDE = (
    # 系统/无回复
    "noreply",
    "no-reply",
    "sentry",
    # 模板/占位邮箱（明显是人编的示例）
    "j.doe",
    "john.doe",
    "jane.doe",
    "test@",
    "@test.",
    "someone@",
    "your-email",
    "yourname",
    "your.name",
    "your.email",
    "name@example",
    "email@example",
    "@example.",
    "@domain.",
    "xxx@",
    # 图片/静态资源误识别
    "@2x",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".gif",
)


class EmailSearcher:
    """搜「公司名 + email」，从搜索结果摘要/正文中提取邮箱。"""

    async def search(self, company_name: str, website: str = "") -> list[str]:
        if not company_name:
            return []

        query = f'"{company_name}" email contact'
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    SEARCH_URL,
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"query": query, "count": 5, "need_content": True},
                )
            if r.status_code != 200:
                return []
            results = r.json().get("results", [])
        except Exception:  # noqa: BLE001
            return []

        domain = ""
        if website:
            domain = (
                website.replace("https://", "")
                .replace("http://", "")
                .split("/")[0]
                .replace("www.", "")
                .lower()
            )

        matched: list[str] = []
        others: list[str] = []
        for item in results:
            text = " ".join(
                [
                    item.get("title") or "",
                    item.get("snippet") or "",
                    item.get("summary") or "",
                    item.get("content") or "",
                ]
            )
            for email in EMAIL_RE.findall(text):
                low = email.lower()
                if any(x in low for x in EXCLUDE) or len(email) > 100:
                    continue
                if domain and domain in low:
                    if email not in matched:
                        matched.append(email)
                elif email not in others:
                    others.append(email)

        return (matched + others)[:3]
