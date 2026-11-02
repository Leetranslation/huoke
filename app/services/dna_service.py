"""企业 DNA 分析：爬官网 → LLM 抽取产品与目标客户（异步）。"""

import re

import httpx

from app.agent.llm import LLMClient
from app.agent.profiler import Profiler
from app.agent.prompts import DNA_SYSTEM, build_dna_prompt
from app.models import Campaign

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class DnaService:
    """分析销售方官网，产出企业 DNA（产品 + 目标客户 + 搜索关键词）。"""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def analyze(self, campaign: Campaign) -> dict:
        content = await self._fetch_site(campaign.website)
        if not content:
            raise ValueError("无法抓取官网内容（网址为空或访问失败）")

        text = await self._llm.chat(
            [
                {"role": "system", "content": DNA_SYSTEM},
                {
                    "role": "user",
                    "content": build_dna_prompt(
                        campaign.name, campaign.website, content
                    ),
                },
            ]
        )
        dna = Profiler._parse(text)
        if not dna:
            raise ValueError("DNA JSON 解析失败")
        dna.setdefault("product_name", campaign.product_name or campaign.name)
        return dna

    @staticmethod
    async def _fetch_site(url: str) -> str:
        """抓官网正文：优先 DeepSeek Fetch，失败回退 httpx。"""
        if not url or not url.startswith("http"):
            return ""

        from app.datasources.deepseek_fetcher import DeepSeekFetcher

        text = await DeepSeekFetcher().fetch(url)
        if text:
            return text[:6000]

        try:
            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=True,
                headers={"User-Agent": UA},
            ) as client:
                r = await client.get(url)
            r.raise_for_status()
            raw = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
            raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.S | re.I)
            raw = re.sub(r"<[^>]+>", " ", raw)
            raw = re.sub(r"\s+", " ", raw)
            return raw.strip()[:6000]
        except Exception:  # noqa: BLE001
            return ""
