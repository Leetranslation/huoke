"""测试邮件追踪：发信 → 模拟打开/点击 → 检查事件。"""

import sys

import httpx

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Contact, Email, EmailEvent
from app.models.enums import EmailStatus
from app.senders.smtp_sender import SMTPSender
from app.services.send_service import SendService

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    db = SessionLocal()
    try:
        contact = db.query(Contact).filter(Contact.company_id == 95).first()
        if contact is None:
            print("没有联系人，跳过")
            return
        # 测试用：改成自己的收件箱（QQ 限制新账号发外部域）
        contact.email = "3793458109@qq.com"
        db.commit()

        email = Email(
            campaign_id=9,
            company_id=95,
            contact_id=contact.id,
            subject="YXAgent 追踪测试",
            body=(
                "Hi there,\n\nThis is a tracking test from YXAgent.\n"
                "Please visit https://example.com/products for details.\n\nBest regards"
            ),
            status=EmailStatus.APPROVED,
        )
        db.add(email)
        db.commit()
        db.refresh(email)

        result = SendService(db, SMTPSender()).send(email)
        print("发送:", result.ok, result.message)
        print("token:", email.tracking_token)

        base = settings.public_base_url.rstrip("/")
        r = httpx.get(f"{base}/t/o/{email.tracking_token}.png", timeout=10)
        print(f"像素请求: {r.status_code} | {r.headers.get('content-type')} | {len(r.content)} bytes")

        r2 = httpx.get(
            f"{base}/t/c/{email.tracking_token}",
            params={"u": "https://example.com/products"},
            follow_redirects=False,
            timeout=10,
        )
        print(f"点击请求: {r2.status_code} -> {r2.headers.get('location')}")

        events = db.query(EmailEvent).filter(EmailEvent.email_id == email.id).all()
        print(f"事件数: {len(events)}")
        for e in events:
            print(f"  - {e.event_type} | {e.meta}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
