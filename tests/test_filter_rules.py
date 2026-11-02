"""验证爬取过滤与邮箱分级规则。"""

import sys

from app.api.routes.campaigns import _looks_like_article, _rank_emails

sys.stdout.reconfigure(encoding="utf-8")

ARTICLES = [
    "Governor Meyer Announces $380M Advanced Manufacturing, Clean Energy Project Joins Jobsfirst Permitting Accelerator",
    "University of Dayton Research Institute",
    "412TH TEST WING TEST CAPABILITIES",
    "What is OEM (original equipment manufacturer)?",
    "Top 10 hydraulic suppliers in Germany",
    "Acme Hydraulics Appoints New CEO",
]
COMPANIES = [
    "Maxpro Technologies",
    "Hans Hydraulik GmbH",
    "Offshore Operator",
]

EMAILS_IN = [
    "hr@genlp.com",
    "notify@dayforce.com",
    "m@udayton.edu",
    "s@udayton.edu",
    "info@worldenergy.org",
    "purchasing@acme-hydraulics.com",
    "sales@acme-hydraulics.com",
    "john.doe@acme-hydraulics.com",
    "noreply@acme-hydraulics.com",
    "privacy@acme-hydraulics.com",
    "buyer@medigruen.de",
]


def main() -> None:
    print("=== 文章/机构过滤 ===")
    for n in ARTICLES:
        r = _looks_like_article(n)
        print(f"{'PASS' if r else 'FAIL'} | 应过滤 | {n[:60]}")

    print("\n=== 正常公司名应保留 ===")
    for n in COMPANIES:
        r = _looks_like_article(n)
        print(f"{'PASS' if not r else 'FAIL'} | 应保留 | {n}")

    print("\n=== 邮箱分级（过滤无用 + 采购优先）===")
    out = _rank_emails(EMAILS_IN)
    for e in out:
        print(f"  {e}")
    bad = {"hr@genlp.com", "notify@dayforce.com", "m@udayton.edu", "s@udayton.edu",
           "noreply@acme-hydraulics.com", "privacy@acme-hydraulics.com"}
    leaked = bad & set(out)
    print(f"\n{'PASS' if not leaked else 'FAIL'} | 无用邮箱已剔除 {leaked or ''}")
    print(f"{'PASS' if out and out[0].startswith(('purchas', 'procure', 'sourcing', 'buyer', 'sales@', 'info@')) else 'FAIL'} | 首位是采购类：{out[0] if out else '无'}")


if __name__ == "__main__":
    main()
