"""M3 真实调用验证：调 DeepSeek 对 2 家公司做画像，人工检查质量。"""

import asyncio

from app.agent.llm import LLMClient
from app.agent.profiler import Profiler


async def main() -> None:
    llm = LLMClient()
    profiler = Profiler(llm)
    samples = [
        ("Acme Industrial GmbH", "https://acme-industrial.de", "Germany", "Industrial machinery"),
        ("Nordic Lighting AS", "https://nordic-lighting.no", "Norway", "Lighting"),
    ]
    for name, website, country, industry in samples:
        p = await profiler.profile(name, website, country, industry, "LED light")
        print("=" * 40)
        print("公司:", name)
        print("行业:", p.industry)
        print("规模:", p.size)
        print("需求信号:", p.demand_signals)
        print("匹配分:", p.match_score)
        print("理由:", p.match_reason)


if __name__ == "__main__":
    asyncio.run(main())
