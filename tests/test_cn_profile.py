"""测试中文画像 + 公司名译名（真调 DeepSeek，约 0.01 元）。"""

import asyncio
import sys

from app.agent.llm import LLMClient
from app.agent.profiler import Profiler

sys.stdout.reconfigure(encoding="utf-8")


async def main() -> None:
    p = Profiler(LLMClient())
    profile = await p.profile(
        "MAILINGER Innovative fiber solutions GmbH",
        "http://www.mailinger.de/",
        "Germany",
        "manufacturer",
        "ERP system",
    )
    print("name_zh:", profile.name_zh)
    print("industry:", profile.industry)
    print("desc:", profile.business_description)
    print("signals:", " | ".join(profile.demand_signals))
    print("reason:", profile.match_reason)
    print("score:", profile.match_score)


if __name__ == "__main__":
    asyncio.run(main())
