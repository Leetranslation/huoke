"""调试 check_replies 匹配流程。"""

import sys

from sqlalchemy import func

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Contact, Email
from app.models.enums import EmailStatus
from app.services.imap_service import fetch_replies

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    import redis as redis_lib

    db = SessionLocal()
    client = redis_lib.from_url(settings.redis_url, decode_responses=True)
    replies = fetch_replies(30)
    print("replies:", len(replies))
    for r in replies:
        key = f"yxagent:reply:{r['uid']}"
        if client.get(key):
            print(f"  [跳过] 已处理: {r['from']} uid={r['uid']}")
            continue
        contact = (
            db.query(Contact)
            .filter(func.lower(Contact.email) == r["from"])
            .first()
        )
        print(
            f"  from={r['from']!r} -> contact={contact.id if contact else None}"
        )
        if contact is None:
            continue
        last_email = (
            db.query(Email)
            .filter(Email.contact_id == contact.id, Email.status == EmailStatus.SENT)
            .order_by(Email.id.desc())
            .first()
        )
        print(f"    last_email={last_email.id if last_email else None}")
    db.close()


if __name__ == "__main__":
    main()
