"""测试邮箱占位过滤规则。"""

import sys

from app.datasources.email_searcher import EXCLUDE

sys.stdout.reconfigure(encoding="utf-8")

CASES = [
    ("j.doe@tscms.com", True),
    ("john.doe@tscms.com", True),
    ("test@company.com", True),
    ("someone@example.com", True),
    ("yourname@gmail.com", True),
    ("xxx@abc.com", True),
    ("sales@maxprotech.com", False),
    ("info@medigruen.com", False),
    ("Hans.Pfitzmaier@de.linde-gas.com", False),
    ("parts@messer-cs.de", False),
]


def main() -> None:
    failed = 0
    for email, should_exclude in CASES:
        low = email.lower()
        excluded = any(x in low for x in EXCLUDE)
        ok = excluded == should_exclude
        if not ok:
            failed += 1
        print(f"{'PASS' if ok else 'FAIL'} | {email:38} | 过滤={excluded} | 预期={should_exclude}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} 通过")


if __name__ == "__main__":
    main()
