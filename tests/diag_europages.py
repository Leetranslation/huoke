"""测试 Europages 数据源可用性。"""

import sys

from app.datasources.europages_source import EuropagesDataSource

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    for q in ["hydrogen equipment", "hydraulic components"]:
        print(f"\n=== 「{q}」 ===")
        try:
            src = EuropagesDataSource(q, max_companies=5)
            raws = src.fetch()
            print(f"返回 {len(raws)} 条：")
            for r in raws:
                print(f"   {r.name[:45]:45} | {r.website[:60] if r.website else '-'} | {r.country}")
        except Exception as e:  # noqa: BLE001
            print(f"失败: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
