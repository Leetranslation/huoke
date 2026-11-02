"""跟进状态机决策（LangGraph），不依赖数据库与网络。"""

import pytest

from app.agent.graph import SEND, STOP, WAIT, FollowUpGraph
from app.models.enums import ContactStatus


@pytest.fixture
def graph() -> FollowUpGraph:
    return FollowUpGraph(follow_up_interval_days=4)


class TestTerminalStates:
    """终止态：无论多久、第几步，都停止。"""

    @pytest.mark.parametrize(
        "lifecycle",
        [
            ContactStatus.REPLIED,
            ContactStatus.COMPLETED,
            ContactStatus.REJECTED,
            ContactStatus.UNSUBSCRIBED,
            ContactStatus.INVALID,
        ],
    )
    def test_terminal_always_stop(self, graph, lifecycle):
        assert graph.decide(lifecycle, step_no=1, max_steps=5, days_since_last=99) == STOP


class TestFirstTouch:
    """首次触达：待触达 / 已确认 → 直接发送。"""

    @pytest.mark.parametrize("lifecycle", [ContactStatus.PENDING, ContactStatus.QUALIFIED])
    def test_first_send(self, graph, lifecycle):
        assert graph.decide(lifecycle, step_no=0, max_steps=5) == SEND


class TestFollowUpInterval:
    """跟进中：只有超过间隔天数才发下一封。"""

    def test_wait_before_interval(self, graph):
        assert graph.decide(ContactStatus.CONTACTED, 1, 5, days_since_last=3) == WAIT

    def test_send_on_interval(self, graph):
        assert graph.decide(ContactStatus.CONTACTED, 1, 5, days_since_last=4) == SEND

    def test_send_after_interval(self, graph):
        assert graph.decide(ContactStatus.CONTACTED, 2, 5, days_since_last=10) == SEND


class TestMaxSteps:
    """达到轮次上限后不再跟进，即使客户还在跟进中。"""

    def test_stop_at_limit(self, graph):
        assert graph.decide(ContactStatus.CONTACTED, 5, 5, days_since_last=99) == STOP

    def test_stop_over_limit(self, graph):
        assert graph.decide(ContactStatus.CONTACTED, 6, 5, days_since_last=99) == STOP


class TestUnknownLifecycle:
    def test_unknown_stops(self, graph):
        assert graph.decide("weird_status", 1, 5, days_since_last=99) == STOP
