"""模拟邮件发送：不真发，只记录日志。用于开发/演示/单测。"""

import logging

from app.senders.base import EmailSender, SendResult

logger = logging.getLogger(__name__)


class MockEmailSender(EmailSender):
    def send(self, to: str, subject: str, body: str, html: str = "") -> SendResult:
        logger.info("mock send | to=%s | subject=%s", to, subject)
        return SendResult(ok=True, message="mock sent")
