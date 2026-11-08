"""诊断：直接在 Python 层调 EmailService，抓完整异常堆栈。"""

import asyncio
import sys
import time
import traceback

from app.agent.email_writer import EmailWriter
from app.agent.llm import LLMClient
from app.agent.prompts import EMAIL_SYSTEM, build_email_prompt
from app.core.database import SessionLocal
from app.models import Campaign, Company, Contact
from app.services.email_service import EmailService

sys.stdout.reconfigure(encoding="utf-8")

COMPANY_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 151
CONTACT_ID = int(sys.argv[2]) if len(sys.argv) > 2 else 91


async def main() -> None:
    db = SessionLocal()
    company = db.get(Company, COMPANY_ID)
    contact = db.get(Contact, CONTACT_ID)
    campaign = db.get(Campaign, company.campaign_id)

    prof = company.profile or {}
    prompt = build_email_prompt(
        campaign.product_name, company.name, prof, contact.name, contact.title
    )
    print(f"EMAIL_SYSTEM 长度: {len(EMAIL_SYSTEM)} 字符")
    print(f"用户 prompt 长度: {len(prompt)} 字符")
    print(f"prompt 前 200 字: {prompt[:200]}\n")

    writer = EmailWriter(LLMClient())
    t = time.time()
    try:
        email = await EmailService(db, writer).generate(
            company, contact, campaign.product_name
        )
        print(f"成功 {time.time()-t:.1f}s | email_id={email.id}")
        print(f"主题: {email.subject}")
    except Exception:  # noqa: BLE001
        print(f"失败 {time.time()-t:.1f}s")
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
