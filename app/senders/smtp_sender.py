"""SMTP 邮件发送：用 smtplib 发真实邮件（QQ/163/企业邮箱通用，支持 HTML）。"""

import logging
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

from app.core.config import settings
from app.senders.base import EmailSender, SendResult

logger = logging.getLogger(__name__)


class SMTPSender(EmailSender):
    """真实 SMTP 发信。配置项：SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD。"""

    def __init__(self):
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._user = settings.smtp_user
        self._password = settings.smtp_password

    def send(self, to: str, subject: str, body: str, html: str = "") -> SendResult:
        if not self._host or not self._user or not self._password:
            return SendResult(ok=False, message="SMTP 未配置（缺 HOST/USER/PASSWORD）")

        msg = MIMEText(html or body, "html" if html else "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        # QQ/163 要求 From 必须等于登录账号
        msg["From"] = formataddr(("YXAgent", self._user))
        msg["To"] = to

        try:
            if self._port == 465:
                server = smtplib.SMTP_SSL(self._host, self._port, timeout=25)
            else:
                server = smtplib.SMTP(self._host, self._port, timeout=25)
                server.starttls()
            server.login(self._user, self._password)
            server.sendmail(self._user, [to], msg.as_string())
            server.quit()
            logger.info("邮件已发送 -> %s | %s", to, subject)
            return SendResult(ok=True, message="sent")
        except Exception as e:  # noqa: BLE001
            logger.warning("邮件发送失败 -> %s: %s", to, e)
            return SendResult(ok=False, message=str(e))
