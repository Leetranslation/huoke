"""验证爬取后自动注入测试客户。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    cid = 9
    r = httpx.post(f"http://127.0.0.1:8001/campaigns/{cid}/crawl", timeout=180)
    print("crawl:", r.status_code)
    if r.status_code != 200:
        print(r.text[:400])
        return
    print(f"新增 {len(r.json())} 个公司")

    r2 = httpx.get(f"http://127.0.0.1:8001/campaigns/{cid}/companies", timeout=30)
    for co in r2.json():
        if co.get("source") == "test":
            print(f"测试客户: {co['name']} | identity={co['identity']}")


if __name__ == "__main__":
    main()
