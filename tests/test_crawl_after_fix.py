"""验证过滤修复：再爬一次，看新线索质量。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8001"
CID = int(sys.argv[1]) if len(sys.argv) > 1 else 9


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=300)
    before = {x["id"] for x in c.get(f"/campaigns/{CID}/companies").json()}

    r = c.post(f"/campaigns/{CID}/crawl", params={"count": 2, "source": "deepseek"})
    if r.status_code != 200:
        print("爬取失败:", r.status_code, r.text[:200])
        return
    new = r.json()
    print(f"新增 {len(new)} 家：")
    for x in new:
        print(f"  - {x['name'][:70]} | 国家={x['country'] or '-'} | {x['identity']}")

    after = {x["id"] for x in c.get(f"/campaigns/{CID}/companies").json()}
    print(f"\n库内公司：{len(before)} → {len(after)}")

    bad = [x for x in new if len(x["name"]) > 60 or "University" in x["name"] or "Announces" in x["name"]]
    print(f"{'PASS' if not bad else 'FAIL'} | 无长标题/机构混入（{len(bad)} 条异常）")

    c.close()


if __name__ == "__main__":
    main()
