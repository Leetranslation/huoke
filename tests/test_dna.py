"""测试企业 DNA 分析（真调 LLM，约 0.01 元）。"""

import asyncio
import sys

from app.agent.llm import LLMClient
from app.models import Campaign
from app.services.dna_service import DnaService

sys.stdout.reconfigure(encoding="utf-8")


async def main() -> None:
    campaign = Campaign(
        name="ERP 出海",
        website="https://www.hytechpaas.com/",
        product_name="ERP system",
    )
    dna = await DnaService(LLMClient()).analyze(campaign)
    print("product_name:", dna.get("product_name"))
    print("product_category:", dna.get("product_category"))
    print("value_proposition:", dna.get("value_proposition"))
    print("applications:", dna.get("applications"))
    print("customer_types:", dna.get("customer_types"))
    print("target_industries:", dna.get("target_industries"))
    print("search_keywords:", dna.get("search_keywords"))


if __name__ == "__main__":
    asyncio.run(main())
