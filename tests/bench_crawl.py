"""基准测试：爬取 / 提取联系人的耗时（打 8011 上的新后端）。"""

import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8011"
CID = int(sys.argv[1]) if len(sys.argv) > 1 else 9


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=400)

    print("=== 爬取线索（并发 5）===")
    t = time.time()
    r = c.post(f"/campaigns/{CID}/crawl", params={"count": 2, "source": "tavily"})
    print(f"耗时 {time.time()-t:.1f}s | status={r.status_code} | 新增 {len(r.json()) if r.status_code==200 else 0} 家")

    print("\n=== 提取联系人（并发 10）===")
    t = time.time()
    r = c.post(f"/campaigns/{CID}/extract-contacts")
    cost = time.time() - t
    if r.status_code == 200:
        d = r.json()
        print(f"耗时 {cost:.1f}s | 新增 {d['created']} 位 / {d['companies']} 家")
    else:
        print(f"耗时 {cost:.1f}s | 失败 {r.status_code}")

    c.close()


if __name__ == "__main__":
    main()
