"""诊断：单家公司的联系人提取耗时（定位瓶颈）。"""

import asyncio
import sys
import time

from app.datasources.contact_extractor import ContactExtractor
from app.datasources.deepseek_fetcher import DeepSeekFetcher

sys.stdout.reconfigure(encoding="utf-8")

URLS = [
    "https://www.maximator.de/",
    "https://www.lhyfe.com/",
    "https://www.schaeffler.com/",
]


async def main() -> None:
    print("=== DeepSeekFetcher 单次抓取 ===")
    f = DeepSeekFetcher()
    for url in URLS[:2]:
        t = time.time()
        text = await f.fetch(url)
        print(f"  {url} → {time.time()-t:.1f}s, {len(text)} 字符")

    print("\n=== ContactExtractor 单家提取（3 页并发）===")
    e = ContactExtractor()
    for url in URLS:
        t = time.time()
        r = await e.extract(url, max_emails=3)
        print(f"  {url} → {time.time()-t:.1f}s, {len(r)} 个邮箱 {[x.email for x in r][:2]}")


if __name__ == "__main__":
    asyncio.run(main())
