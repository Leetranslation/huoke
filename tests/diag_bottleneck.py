"""定位瓶颈：Tavily 搜索 / LLM 实体抽取 / 邮箱搜索 各自耗时。"""

import asyncio
import sys
import time

from app.agent.entity_extractor import EntityExtractor
from app.agent.llm import LLMClient
from app.datasources.email_searcher import EmailSearcher
from app.datasources.tavily_source import TavilyDataSource

sys.stdout.reconfigure(encoding="utf-8")


async def main() -> None:
    llm = LLMClient()

    print("=== 1. Tavily 单次搜索 ===")
    for q in ["hydraulic components manufacturer Germany", "oil and gas equipment supplier USA"]:
        t = time.time()
        src = TavilyDataSource(q, count=4)
        await asyncio.to_thread(src.fetch)
        print(f"  {q[:38]:38} → {time.time()-t:.1f}s, {len(src.raw_results)} 条原始结果")

    print("\n=== 2. LLM 实体抽取单次 ===")
    src = TavilyDataSource("hydraulic components manufacturer Germany", count=4)
    await asyncio.to_thread(src.fetch)
    ex = EntityExtractor(llm)
    t = time.time()
    items = await ex.extract(src.raw_results)
    print(f"  抽取 {time.time()-t:.1f}s, {len(items)} 家：{[x['name'] for x in items][:3]}")

    print("\n=== 3. Tavily 并发 5 次（模拟爬取）===")
    qs = [f"hydraulic supplier Germany variant {i}" for i in range(5)]
    t = time.time()
    await asyncio.gather(*[asyncio.to_thread(TavilyDataSource(q, count=4).fetch) for q in qs])
    print(f"  5 次并发 → {time.time()-t:.1f}s")

    print("\n=== 4. EmailSearcher 单次 ===")
    se = EmailSearcher()
    for name, site in [("Maxpro Technologies", "https://www.maxprotech.com"), ("Stauff GmbH", "https://www.stauff.com")]:
        t = time.time()
        try:
            emails = await se.search(name, site)
            print(f"  {name[:24]:24} → {time.time()-t:.1f}s, {len(emails)} 个邮箱 {emails[:2]}")
        except Exception as e:  # noqa: BLE001
            print(f"  {name[:24]:24} → {time.time()-t:.1f}s, 异常 {type(e).__name__}")


if __name__ == "__main__":
    asyncio.run(main())
