"""测试 Tavily + exclude_domains 效果。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

KEY = "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"
URL = "https://api.tavily.com/search"

EXCLUDE = [
    "yahoo.com", "cnbc.com", "bbc.com", "bbc.co.uk", "reuters.com", "forbes.com",
    "bloomberg.com", "ft.com", "wsj.com", "nytimes.com", "cnn.com",
    "tracxn.com", "crunchbase.com", "cbinsights.com", "zoominfo.com", "pitchbook.com",
    "owler.com", "dnb.com", "investing.com", "marketscreener.com", "morningstar.com",
    "linkedin.com", "wikipedia.org", "youtube.com", "facebook.com", "twitter.com",
    "hyfindr.com", "prnewswire.com", "businesswire.com", "globenewswire.com",
    "amazon.com", "alibaba.com", "indeed.com", "glassdoor.com",
]


def search(q: str, n: int = 8) -> list[dict]:
    r = httpx.post(
        URL,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={
            "query": q,
            "max_results": n,
            "search_depth": "basic",
            "exclude_domains": EXCLUDE,
        },
        timeout=40,
    )
    if r.status_code != 200:
        print("ERR", r.status_code, r.text[:200])
        return []
    return r.json().get("results", [])


def main() -> None:
    for q in [
        "hydrogen production company Germany official site",
        "hydraulic components manufacturer Germany",
    ]:
        print(f"\n=== 「{q}」 ===")
        for x in search(q):
            print(f"  {x['title'][:52]:52} | {x['url'][:62]}")


if __name__ == "__main__":
    main()
