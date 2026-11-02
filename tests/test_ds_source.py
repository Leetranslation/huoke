"""测试 DeepSeek Search 数据源（带国家 query）。"""

import sys

from app.datasources.deepseek_search_source import DeepSeekSearchDataSource

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    for c in DeepSeekSearchDataSource("manufacturer Germany industrial", count=5).fetch():
        print(f"{c.name} | {c.website}")
        print(f"  desc: {(c.description or '')[:100]}")


if __name__ == "__main__":
    main()
