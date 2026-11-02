"""测试 Tavily 搜索 API。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

KEY = "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"
URL = "https://api.tavily.com/search"


def search(q: str, n: int = 6) -> dict:
    r = httpx.post(
        URL,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={"query": q, "max_results": n, "search_depth": "basic"},
        timeout=40,
    )
    return {"status": r.status_code, "body": r.json() if r.status_code == 200 else r.text[:300]}


def main() -> None:
    for q in [
        "hydrogen production company Germany",
        "hydrogen refueling station operator company",
    ]:
        print(f"\n=== 「{q}」 ===")
        res = search(q)
        print("status:", res["status"])
        if res["status"] != 200:
            print(res["body"])
            continue
        data = res["body"]
        for x in data.get("results", []):
            print(f"  {x['title'][:50]:50} | {x['url'][:60]}")


if __name__ == "__main__":
    main()
