"""诊断：看爬取原始候选与过滤结果。"""

import sys

from app.api.routes.campaigns import _looks_like_article
from app.core.database import SessionLocal
from app.datasources.deepseek_search_source import DeepSeekSearchDataSource
from app.models import Campaign

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    db = SessionLocal()
    camp = db.get(Campaign, 9)
    dna = camp.dna or {}
    types = dna.get("customer_types") or []
    kws: list[str] = []
    for t in types:
        if isinstance(t, dict):
            kws.extend(t.get("keywords") or [])

    print(f"任务：{camp.name}")
    print(f"关键词：{kws[:5]}\n")

    for query in kws[:2]:
        print(f"=== 搜索「{query}」 ===")
        raws = DeepSeekSearchDataSource(query, count=5).fetch()
        print(f"数据源返回 {len(raws)} 条：")
        for r in raws:
            flag = "过滤" if _looks_like_article(r.name) else "保留"
            print(f"  [{flag}] {r.name[:68]} | {r.website or '-'}")
        print()

    db.close()


if __name__ == "__main__":
    main()
