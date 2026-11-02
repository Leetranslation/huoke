"""从搜索结果中抽取公司实体（LLM）。

搜索引擎返回的是「网页」，不是「公司」。这一步让 LLM 判断哪些网页属于
真实企业，并提取规范化的公司名，过滤掉行业文章 / 目录站 / 机构 / 栏目页。
"""

import json
import logging

from app.agent.llm import LLMClient
from app.agent.prompts import ENTITY_EXTRACT_SYSTEM, build_entity_prompt

logger = logging.getLogger(__name__)


class EntityExtractor:
    """把搜索结果清洗成公司列表。"""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def extract(self, results: list[dict]) -> list[dict]:
        """results 为搜索原始结果；返回 [{name, website, country}]。"""
        if not results:
            return []

        try:
            text = await self._llm.chat(
                [
                    {"role": "system", "content": ENTITY_EXTRACT_SYSTEM},
                    {"role": "user", "content": build_entity_prompt(results)},
                ]
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("实体抽取调用失败: %s", e)
            return []

        data = self._parse(text)
        companies: list[dict] = []
        for item in data.get("companies") or []:
            if not isinstance(item, dict):
                continue
            idx = item.get("idx")
            name = (item.get("name") or "").strip()
            if not isinstance(idx, int) or not (0 <= idx < len(results)):
                continue
            if not name or len(name) > 60:
                continue
            companies.append(
                {
                    "name": name,
                    "website": (results[idx].get("url") or "").strip(),
                    "country": (item.get("country") or "").strip(),
                    "description": (results[idx].get("content") or "").strip()[:1000],
                }
            )
        return companies

    @staticmethod
    def _parse(text: str) -> dict:
        text = (text or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            s, e = text.find("{"), text.rfind("}")
            if s != -1 and e != -1:
                try:
                    return json.loads(text[s : e + 1])
                except json.JSONDecodeError:
                    pass
            logger.warning("实体抽取 JSON 解析失败: %s", text[:200])
            return {}
