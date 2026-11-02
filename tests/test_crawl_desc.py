"""验证爬虫是否提取到业务描述。"""

import sys

from app.datasources.europages_source import EuropagesDataSource

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    for c in EuropagesDataSource("manufacturer germany", max_companies=2).fetch():
        print("name:", c.name)
        print("country:", c.country)
        print("desc:", (c.description or "(空)")[:300])
        print("-" * 50)


if __name__ == "__main__":
    main()
