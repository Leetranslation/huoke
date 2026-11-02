"""IMAP 收信：拉取收件箱、识别客户回复。"""

import email
import imaplib
import logging
import re
from email.header import decode_header

from app.core.config import settings

logger = logging.getLogger(__name__)

IMAP_HOST = "imap.163.com"
IMAP_PORT = 993

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def _decode(s: str) -> str:
    if not s:
        return ""
    parts = decode_header(s)
    out: list[str] = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def _extract_email(addr: str) -> str:
    m = EMAIL_RE.search(addr or "")
    return m.group(0).lower() if m else ""


def _extract_body(msg) -> str:
    """从邮件中提取纯文本正文。"""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                try:
                    return payload.decode(charset, errors="replace")
                except Exception:  # noqa: BLE001
                    return payload.decode("utf-8", errors="replace")
        return ""
    payload = msg.get_payload(decode=True)
    if not payload:
        return ""
    charset = msg.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except Exception:  # noqa: BLE001
        return payload.decode("utf-8", errors="replace")


def fetch_replies(limit: int = 30) -> list[dict]:
    """拉取最近 limit 封邮件，解析为回复列表（发件人/主题/正文/时间/UID）。"""
    if not (settings.smtp_user and settings.smtp_password):
        return []

    try:
        conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        conn.login(settings.smtp_user, settings.smtp_password)
        # 163 要求登录后发送 ID 命令标识客户端，否则 SELECT 被拒
        imaplib.Commands["ID"] = ("AUTH",)
        conn._simple_command("ID", '("name" "YXAgent" "version" "1.0" "vendor" "YXAgent")')
        conn.select("INBOX")
        typ, data = conn.search(None, "ALL")
        ids = data[0].split()[-limit:]
        replies: list[dict] = []
        for i in reversed(ids):
            typ, msg_data = conn.fetch(i, "(RFC822)")
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            from_addr = _extract_email(_decode(msg["From"] or ""))
            if not from_addr:
                continue
            replies.append(
                {
                    "from": from_addr,
                    "subject": _decode(msg["Subject"] or ""),
                    "date": msg["Date"] or "",
                    "body": _extract_body(msg).strip(),
                    "uid": i.decode() if isinstance(i, bytes) else str(i),
                }
            )
        conn.logout()
        return replies
    except Exception as e:  # noqa: BLE001
        logger.warning("IMAP 拉取失败: %s", e)
        return []
