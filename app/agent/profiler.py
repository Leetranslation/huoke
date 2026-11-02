"""画像抽取与匹配评分（AI 核心之一）。

评分逻辑：LLM 只输出 6 个维度的分数与理由，后端按固定权重计算总分。
这样分数可解释、可复现，而不是让 LLM 直接自由拍一个总分。
"""

import json
import logging
from dataclasses import dataclass, field

from app.agent.llm import LLMClient
from app.agent.prompts import PROFILE_SYSTEM, build_profile_prompt

logger = logging.getLogger(__name__)

# 评分维度与权重（调整权重即视为升级评分版本）
SCORE_WEIGHTS: dict[str, float] = {
    "product_application": 0.30,  # 产品与应用匹配度
    "industry": 0.20,             # 行业匹配度
    "buyer_type": 0.15,           # 买家类型匹配度
    "target_market": 0.10,        # 目标市场匹配度
    "procurement_fit": 0.10,      # 企业采购适配能力
    "demand_signal": 0.15,        # 公开需求信号
}


@dataclass
class CompanyProfile:
    name_zh: str = ""
    industry: str = ""
    business_description: str = ""
    size: str = ""
    demand_signals: list[str] = field(default_factory=list)
    dimensions: dict = field(default_factory=dict)
    match_score: float = 0.0
    match_reason: str = ""


class Profiler:
    """用 LLM 抽取画像，并以后端加权规则计算匹配分。"""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def profile(
        self,
        company_name: str,
        website: str,
        country: str,
        industry: str,
        product: str,
        description: str = "",
    ) -> CompanyProfile:
        messages = [
            {"role": "system", "content": PROFILE_SYSTEM},
            {
                "role": "user",
                "content": build_profile_prompt(
                    company_name, website, country, industry, product, description
                ),
            },
        ]
        text = await self._llm.chat(messages)
        data = self._parse(text)
        dimensions = data.get("dimensions", {}) or {}
        return CompanyProfile(
            name_zh=data.get("name_zh", ""),
            industry=data.get("industry", ""),
            business_description=data.get("business_description", ""),
            size=data.get("size", ""),
            demand_signals=data.get("demand_signals", []),
            dimensions=dimensions,
            match_score=self.compute_score(dimensions),
            match_reason=data.get("match_reason", ""),
        )

    @staticmethod
    def compute_score(dimensions: dict) -> float:
        """按固定权重汇总各维度分数，得到 0-100 总分。"""
        total = 0.0
        for key, weight in SCORE_WEIGHTS.items():
            dim = dimensions.get(key) or {}
            try:
                score = float(dim.get("score", 0))
            except (TypeError, ValueError):
                score = 0.0
            total += max(0.0, min(100.0, score)) * weight
        return round(total, 1)

    @staticmethod
    def _parse(text: str) -> dict:
        """从 LLM 输出中稳健地解析 JSON（兼容 ```json 包裹、截取）。"""
        text = (text or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    pass
            logger.warning("无法解析画像 JSON: %s", text)
            return {}
