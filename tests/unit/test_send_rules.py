"""发送前的停止规则（不依赖真实数据库与 SMTP）。"""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.models.enums import ContactStatus, EmailStatus
from app.services.send_service import SendService


class FakeSender:
    def __init__(self, ok: bool = True):
        self.ok = ok
        self.sent: list[tuple] = []

    def send(self, to, subject, body, html=None):
        self.sent.append((to, subject))
        return SimpleNamespace(ok=self.ok, message="sent" if self.ok else "failed")


class FakeSession:
    def __init__(self, contact=None):
        self._contact = contact
        self.commits = 0

    def get(self, model, pk):
        return self._contact

    def commit(self):
        self.commits += 1


def make_email(status=EmailStatus.APPROVED, sent_at=None):
    return SimpleNamespace(
        id=1,
        contact_id=1,
        subject="Hello",
        body="Body",
        status=status,
        sent_at=sent_at,
        tracking_token=None,
    )


def make_contact(status=ContactStatus.PENDING, email="buyer@example.com"):
    return SimpleNamespace(id=1, status=status, email=email)


class TestStopRules:
    def test_reject_when_not_approved(self):
        svc = SendService(FakeSession(make_contact()), FakeSender())
        result = svc.send(make_email(status=EmailStatus.DRAFT))
        assert not result.ok
        assert "未批准" in result.message

    def test_reject_duplicate_send(self):
        svc = SendService(FakeSession(make_contact()), FakeSender())
        email = make_email(sent_at=datetime.now(timezone.utc))
        result = svc.send(email)
        assert not result.ok
        assert "重复" in result.message

    @pytest.mark.parametrize(
        "status",
        [
            ContactStatus.REPLIED,
            ContactStatus.REJECTED,
            ContactStatus.UNSUBSCRIBED,
            ContactStatus.INVALID,
            ContactStatus.COMPLETED,
        ],
    )
    def test_reject_terminal_contact(self, status):
        svc = SendService(FakeSession(make_contact(status=status)), FakeSender())
        result = svc.send(make_email())
        assert not result.ok
        assert "终止" in result.message


class TestSuccessfulSend:
    def test_send_marks_email_and_contact(self):
        contact = make_contact(status=ContactStatus.PENDING)
        sender = FakeSender()
        session = FakeSession(contact)
        email = make_email()

        result = SendService(session, sender).send(email)

        assert result.ok
        assert email.status == EmailStatus.SENT
        assert email.sent_at is not None
        assert email.tracking_token
        # 待触达 → 跟进中
        assert contact.status == ContactStatus.CONTACTED
        assert sender.sent == [("buyer@example.com", "Hello")]
        assert session.commits == 1

    def test_failed_send_keeps_status(self):
        contact = make_contact()
        email = make_email()
        result = SendService(FakeSession(contact), FakeSender(ok=False)).send(email)

        assert not result.ok
        assert email.status == EmailStatus.APPROVED
        assert contact.status == ContactStatus.PENDING

    def test_qualified_also_becomes_contacted(self):
        contact = make_contact(status=ContactStatus.QUALIFIED)
        SendService(FakeSession(contact), FakeSender()).send(make_email())
        assert contact.status == ContactStatus.CONTACTED
