"""开发信生成（AI 核心之二）。"""

import json
import logging
from dataclasses import dataclass

from app.agent.llm import LLMClient
from app.agent.prompts import (
    EMAIL_SYSTEM,
    FOLLOWUP_SYSTEM,
    build_email_prompt,
    build_followup_prompt,
)

logger = logging.getLogger(__name__)


@dataclass
class EmailDraft:
    subject: str = ""
    body: str = ""


class EmailWriter:
    """用 LLM 基于公司画像生成个性化开发信。"""

    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def write(
        self,
        product: str,
        company_name: str,
        profile: dict,
        contact_name: str = "",
        contact_title: str = "",
        country: str = "",
    ) -> EmailDraft:
        messages = [
            {"role": "system", "content": EMAIL_SYSTEM},
            {
                "role": "user",
                "content": build_email_prompt(
                    product, company_name, profile, contact_name, contact_title, country
                ),
            },
        ]
        text = await self._llm.chat(messages)
        data = self._parse(text)
        return EmailDraft(
            subject=data.get("subject", ""),
            body=data.get("body", ""),
        )

    async def write_followup(
        self,
        product: str,
        company_name: str,
        contact_name: str,
        step_no: int,
        last_subject: str = "",
    ) -> EmailDraft:
        """写跟进邮件（比首封更短，换个角度）。"""
        messages = [
            {"role": "system", "content": FOLLOWUP_SYSTEM},
            {
                "role": "user",
                "content": build_followup_prompt(
                    product, company_name, contact_name, step_no, last_subject
                ),
            },
        ]
        text = await self._llm.chat(messages)
        data = self._parse(text)
        return EmailDraft(
            subject=data.get("subject", ""),
            body=data.get("body", ""),
        )

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
            logger.warning("无法解析邮件 JSON: %s", text)
            return {}
