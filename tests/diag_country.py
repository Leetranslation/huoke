"""查：任务的目标市场 + 库里中国公司的来源。"""

import sys

from sqlalchemy import func

from app.core.database import SessionLocal
from app.models import Campaign, Company

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    db = SessionLocal()

    for cid in (9,):
        c = db.get(Campaign, cid)
        if c:
            print(f"任务 {cid}: {c.name}")
            print(f"  product: {c.product_name}")
            print(f"  target_market: {c.target_market}")
            kws = (c.dna or {}).get("customer_types") or []
            for t in kws[:3]:
                if isinstance(t, dict):
                    print(f"  客户类型: {t.get('name')} | kw: {(t.get('keywords') or [])[:3]}")

    print("\n=== 中国相关公司 ===")
    rows = (
        db.query(Company)
        .filter(
            func.lower(Company.country).in_(["china", "cn", "中国", "prc"])
        )
        .order_by(Company.id.desc())
        .limit(12)
        .all()
    )
    for x in rows:
        print(f"  id={x.id} task={x.campaign_id} | {x.name[:40]} | {x.country} | {x.identity} | {x.website[:35] if x.website else '-'}")

    print("\n=== 各国分布 ===")
    dist = (
        db.query(Company.country, func.count(Company.id))
        .group_by(Company.country)
        .order_by(func.count(Company.id).desc())
        .limit(15)
        .all()
    )
    for country, n in dist:
        print(f"  {country or '(空)'}: {n}")

    db.close()


if __name__ == "__main__":
    main()
