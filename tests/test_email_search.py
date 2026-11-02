"""测试用 Search API 搜公司邮箱。"""

import asyncio
import sys

from app.datasources.email_searcher import EmailSearcher

sys.stdout.reconfigure(encoding="utf-8")


async def main() -> None:
    searcher = EmailSearcher()
    cases = [
        ("Maximator GmbH", "https://www.maximator.de/"),
        ("Bogner GmbH & Co. KG", ""),
    ]
    for name, site in cases:
        print(name, "->", await searcher.search(name, site))


if __name__ == "__main__":
    asyncio.run(main())
