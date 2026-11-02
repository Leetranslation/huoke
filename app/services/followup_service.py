"""自动跟进服务：状态机决策 + LLM 回复意图判断 + 记录跟进步骤。"""

import json

from sqlalchemy.orm import Session

from app.agent.graph import FOLLOW_UP_INTERVAL_DAYS, FollowUpGraph
from app.agent.llm import LLMClient
from app.agent.prompts import REPLY_INTENT_SYSTEM, build_intent_prompt
from app.models import Contact, FollowUpStep


class FollowUpService:
    def __init__(
        self,
        session: Session,
        llm: LLMClient | None = None,
        max_steps: int = 5,
        follow_up_interval_days: int = FOLLOW_UP_INTERVAL_DAYS,
    ):
        self._session = session
        self._llm = llm
        self._max_steps = max_steps
        self._graph = FollowUpGraph(follow_up_interval_days)

    def decide(self, contact: Contact, step_no: int, days_since_last: int = 0) -> str:
        """返回下一步动作：send / wait / stop。"""
        return self._graph.decide(
            contact.status, step_no, self._max_steps, days_since_last
        )

    async def classify_reply(self, reply_text: str) -> str:
        """用 LLM 判断回复意图：positive / negative / neutral。"""
        if self._llm is None:
            return "neutral"
        messages = [
            {"role": "system", "content": REPLY_INTENT_SYSTEM},
            {"role": "user", "content": build_intent_prompt(reply_text)},
        ]
        text = await self._llm.chat(messages)
        try:
            data = json.loads(text.strip().strip("`"))
            return data.get("intent", "neutral")
        except (json.JSONDecodeError, AttributeError):
            return "neutral"

    def record_step(
        self,
        contact: Contact,
        step_no: int,
        step_type: str,
        email_id: int | None = None,
    ) -> FollowUpStep:
        step = FollowUpStep(
            company_id=contact.company_id,
            contact_id=contact.id,
            step_no=step_no,
            step_type=step_type,
            email_id=email_id,
        )
        self._session.add(step)
        self._session.commit()
        return step
