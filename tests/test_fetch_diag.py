"""诊断 Fetch 抓取结果与邮箱位置。"""

import asyncio
import re
import sys

from app.datasources.deepseek_fetcher import DeepSeekFetcher

sys.stdout.reconfigure(encoding="utf-8")

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

URLS = [
    "https://www.maximator.de/en/homepage-2123464850.html",
    "https://www.maximator.de/en/contact",
    "https://www.maximator.de/impressum",
    "https://www.maximator.de/en/imprint",
]


async def main() -> None:
    f = DeepSeekFetcher()
    for url in URLS:
        text = await f.fetch(url)
        emails = EMAIL_RE.findall(text or "")
        print(f"{url} | len={len(text)} | emails={emails[:5]}")
        if text:
            print("  前 150 字:", text[:150].replace("\n", " "))


if __name__ == "__main__":
    asyncio.run(main())
