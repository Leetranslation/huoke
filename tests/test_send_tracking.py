"""发一封带公网追踪像素的测试邮件。"""

import sys

from app.core.database import SessionLocal
from app.models import Company, Contact, Email
from app.models.enums import EmailStatus
from app.senders.smtp_sender import SMTPSender
from app.services.send_service import SendService

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    db = SessionLocal()
    try:
        contact = (
            db.query(Contact)
            .filter(Contact.email == "3793458109@qq.com")
            .order_by(Contact.id)
            .first()
        )
        if contact is None:
            print("没有测试联系人")
            return
        company = db.get(Company, contact.company_id)
        email = Email(
            campaign_id=company.campaign_id,
            company_id=company.id,
            contact_id=contact.id,
            subject="追踪验证（公网像素）",
            body=(
                "Hi,\n\nThis is a tracking test email.\n"
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
        print("请打开 QQ 邮箱，打开这封邮件，几秒后查看打开次数")
    finally:
        db.close()


if __name__ == "__main__":
    main()
