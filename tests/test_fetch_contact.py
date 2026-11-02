"""测试 Fetch 集成：用 DeepSeek Fetch 抓官网提取邮箱。"""

import asyncio
import sys

from app.datasources.contact_extractor import ContactExtractor

sys.stdout.reconfigure(encoding="utf-8")


async def main() -> None:
    ex = ContactExtractor(use_deepseek=True)
    urls = [
        "https://www.maximator.de/en/homepage-2123464850.html",
        "https://www.bogner-gmbh.de/",
    ]
    for url in urls:
        emails = [c.email for c in await ex.extract(url)]
        print(f"{url} -> {emails}")


if __name__ == "__main__":
    asyncio.run(main())
