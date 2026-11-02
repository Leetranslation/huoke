"""对比不同查询写法，找能返回真实公司的那个。"""

import sys

from app.datasources.deepseek_search_source import DeepSeekSearchDataSource, EXCLUDE_TITLE

sys.stdout.reconfigure(encoding="utf-8")


def show(query: str) -> None:
    raws = DeepSeekSearchDataSource(query, count=6).fetch()
    print(f'\n=== 「{query}」→ {len(raws)} 条 ===')
    for r in raws:
        print(f"   {r.name[:45]:45} | {r.website[:55]}")


def main() -> None:
    for q in [
        "hydrogen production company",
        "hydrogen production company official website",
        "hydrogen production companies contact email",
        "hydrogen plant operator company site",
    ]:
        show(q)


if __name__ == "__main__":
    main()
