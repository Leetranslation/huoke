"""发送与追踪服务：发送前停止规则校验 + 发送 + 事件记录。

关键设计：
- 打开/点击只作为事件记录，不改变客户生命周期（打开追踪不可靠）
- 发送前执行停止规则：必须人工批准、禁止重复发送、客户终止态禁止发送
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Contact, Email, EmailEvent
from app.models.enums import ContactStatus, EmailStatus, EventType
from app.senders.base import EmailSender, SendResult
from app.services.tracking_service import build_tracked_html, new_token

# 允许从「待触达/已确认」迁移到「跟进中」的前置状态
_SENDABLE = (ContactStatus.PENDING, ContactStatus.QUALIFIED)

# 终止状态：这些客户的邮件禁止发送
_TERMINAL = {
    ContactStatus.REPLIED,
    ContactStatus.COMPLETED,
    ContactStatus.REJECTED,
    ContactStatus.UNSUBSCRIBED,
    ContactStatus.INVALID,
}


class SendService:
    def __init__(self, session: Session, sender: EmailSender):
        self._session = session
        self._sender = sender

    def send(self, email: Email) -> SendResult:
        """发送一封邮件；发送前执行停止规则校验。"""
        # 停止规则 1：禁止重复发送
        if email.sent_at is not None:
            return SendResult(ok=False, message="邮件已发送，禁止重复发送")
        # 停止规则 2：必须人工批准
        if email.status != EmailStatus.APPROVED:
            return SendResult(
                ok=False, message=f"邮件未批准（当前 {email.status}），禁止发送"
            )

        contact = None
        if email.contact_id:
            contact = self._session.get(Contact, email.contact_id)

        # 停止规则 3：客户处于终止态不发
        if contact and contact.status in _TERMINAL:
            return SendResult(
                ok=False, message=f"客户已终止（{contact.status}），禁止发送"
            )

        to = contact.email if contact else ""

        # 生成追踪 token（首次发送时），并注入打开像素 + 点击链接
        if not email.tracking_token:
            email.tracking_token = new_token()
        html = build_tracked_html(email.body, email.tracking_token)

        result = self._sender.send(to, email.subject, email.body, html=html)
        if result.ok:
            email.status = EmailStatus.SENT
            email.sent_at = datetime.now(timezone.utc)
            if contact and contact.status in _SENDABLE:
                contact.status = ContactStatus.CONTACTED
        self._session.commit()
        return result

    def record_event(self, email: Email, event_type: str) -> EmailEvent:
        """记录事件；只有回复/退信/退订/拒绝才改变生命周期，打开/点击不改变。"""
        event = EmailEvent(email_id=email.id, event_type=event_type)
        self._session.add(event)
        if email.contact_id:
            contact = self._session.get(Contact, email.contact_id)
            if contact:
                if event_type == EventType.REPLY:
                    contact.status = ContactStatus.REPLIED
                elif event_type == EventType.BOUNCE:
                    contact.status = ContactStatus.INVALID
                elif event_type == EventType.UNSUBSCRIBE:
                    contact.status = ContactStatus.UNSUBSCRIBED
                elif event_type == EventType.REJECTED:
                    contact.status = ContactStatus.REJECTED
                # open / click / manual_note：只记录事件，不改生命周期
        self._session.commit()
        return event
