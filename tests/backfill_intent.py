"""补跑历史回复的意图识别（把 negative 改成退订）。"""

import asyncio
import sys

from app.agent.llm import LLMClient
from app.core.database import SessionLocal
from app.models import Contact, Email, EmailEvent
from app.models.enums import ContactStatus
from app.services.followup_service import FollowUpService

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    db = SessionLocal()
    service = FollowUpService(db, LLMClient())
    events = (
        db.query(EmailEvent)
        .filter(EmailEvent.event_type == "reply")
        .order_by(EmailEvent.id)
        .all()
    )
    print(f"待处理回复 {len(events)} 条\n")

    for ev in events:
        meta = dict(ev.meta or {})
        email = db.get(Email, ev.email_id)
        contact = db.get(Contact, email.contact_id) if email and email.contact_id else None
        if contact is None:
            continue

        body = (meta.get("body") or "").split("---Original---")[0].strip()[:1200]
        intent = asyncio.run(service.classify_reply(body)) if body else "neutral"
        new_status = (
            ContactStatus.UNSUBSCRIBED if intent == "negative" else ContactStatus.REPLIED
        )

        meta["intent"] = intent
        ev.meta = meta
        old = contact.status
        contact.status = new_status
        db.commit()

        preview = body.replace("\r", " ").replace("\n", " ")[:24]
        print(f"contact={contact.id} 「{preview}」 intent={intent}  {old} → {new_status}")

    print("\n=== 最终状态 ===")
    for c in db.query(Contact).filter(Contact.status.in_(["replied", "unsubscribed"])).all():
        print(f"  id={c.id} {c.status}")
    db.close()


if __name__ == "__main__":
    main()
