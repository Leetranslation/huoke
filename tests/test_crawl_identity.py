"""测试分类型爬取 + 身份分类（直接调 API）。"""

import asyncio
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")


async def main() -> None:
    async with httpx.AsyncClient(timeout=600) as c:
        r = await c.post(
            "http://127.0.0.1:8001/campaigns/6/crawl",
            params={"max_companies": 8, "data_source": "deepseek"},
        )
        print("status:", r.status_code)
        if r.status_code != 200:
            print(r.text[:800])
            return
        companies = r.json()
        print(f"爬取 {len(companies)} 家")
        for co in companies:
            print(f"[{co['identity']}] {co['name']} | {co['website']}")
            print(f"    理由: {(co.get('identity_reason') or '')[:120]}")


if __name__ == "__main__":
    asyncio.run(main())
