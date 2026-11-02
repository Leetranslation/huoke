"""跟进状态机（LangGraph）：基于客户生命周期 + 发送时间决定下一步动作。

关键设计：不使用「是否打开」作为决策依据（打开追踪不可靠），
未回复时按「距上次发送天数」决定是否生成跟进信。
"""

from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.models.enums import ContactStatus

# 动作
SEND = "send"   # 发送（首封或跟进信）
WAIT = "wait"   # 等待（未到跟进间隔）
STOP = "stop"   # 停止（回复/拒绝/退订/无效/达上限）

# 默认跟进间隔（天）：距上次发送超过该天数才生成跟进信
FOLLOW_UP_INTERVAL_DAYS = 4

# 终止状态：不再自动跟进
TERMINAL = {
    ContactStatus.REPLIED,
    ContactStatus.COMPLETED,
    ContactStatus.REJECTED,
    ContactStatus.UNSUBSCRIBED,
    ContactStatus.INVALID,
}


class FollowUpState(TypedDict):
    lifecycle: str
    step_no: int
    max_steps: int
    days_since_last: int
    action: str


class FollowUpGraph:
    """跟进状态机：把「决策 → 发送/等待/停止」串成 LangGraph 图。"""

    def __init__(self, follow_up_interval_days: int = FOLLOW_UP_INTERVAL_DAYS):
        self._interval = follow_up_interval_days
        self._graph = self._build()

    def _build(self):
        g = StateGraph(FollowUpState)

        def decide(state: FollowUpState) -> FollowUpState:
            lifecycle = state["lifecycle"]
            step_no = state["step_no"]
            max_steps = state["max_steps"]
            days = state["days_since_last"]

            if lifecycle in TERMINAL:
                action = STOP
            elif step_no >= max_steps:
                action = STOP
            elif lifecycle in (ContactStatus.PENDING, ContactStatus.QUALIFIED):
                action = SEND          # 首封
            elif lifecycle == ContactStatus.CONTACTED:
                action = SEND if days >= self._interval else WAIT
            else:
                action = STOP

            return {**state, "action": action}

        def noop(state: FollowUpState) -> FollowUpState:
            return state

        g.add_node("decide", decide)
        g.add_node("send", noop)
        g.add_node("wait", noop)
        g.add_node("stop", noop)
        g.set_entry_point("decide")

        def route(state: FollowUpState) -> Literal["send", "wait", "stop"]:
            return state["action"]  # type: ignore[return-value]

        g.add_conditional_edges(
            "decide", route, {"send": "send", "wait": "wait", "stop": "stop"}
        )
        g.add_edge("send", END)
        g.add_edge("wait", END)
        g.add_edge("stop", END)
        return g.compile()

    def decide(
        self,
        lifecycle: str,
        step_no: int,
        max_steps: int,
        days_since_last: int = 0,
    ) -> str:
        result = self._graph.invoke(
            {
                "lifecycle": lifecycle,
                "step_no": step_no,
                "max_steps": max_steps,
                "days_since_last": days_since_last,
                "action": "",
            }
        )
        return result["action"]
