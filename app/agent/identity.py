"""公司身份分类：买家 / 同行 / 无关 / 不明（约 0.005 元/家）。"""

import json
import logging
from dataclasses import dataclass

from app.agent.llm import LLMClient
from app.agent.prompts import IDENTITY_SYSTEM, build_identity_prompt

logger = logging.getLogger(__name__)

VALID_LABELS = {"buyer", "competitor", "irrelevant", "unknown"}


@dataclass
class Identity:
    label: str = "unknown"
    reason: str = ""


class IdentityClassifier:
    """用 LLM 判断一家公司是买家、同行、无关还是不明。"""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def classify(
        self,
        company_name: str,
        summary: str,
        product: str,
        customer_types: list[str],
        exclude_rules: list[str],
    ) -> Identity:
        try:
            text = await self._llm.chat(
                [
                    {"role": "system", "content": IDENTITY_SYSTEM},
                    {
                        "role": "user",
                        "content": build_identity_prompt(
                            company_name, summary, product, customer_types, exclude_rules
                        ),
                    },
                ]
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("身份判断失败 %s: %s", company_name, e)
            return Identity("unknown", "调用失败")

        data = self._parse(text)
        label = (data.get("label") or "unknown").lower()
        if label not in VALID_LABELS:
            label = "unknown"
        return Identity(label=label, reason=(data.get("reason") or "")[:500])

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
            start, end = text.find("{"), text.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    pass
            return {}
