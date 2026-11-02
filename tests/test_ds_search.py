"""测试 DeepSeek Search API 返回结构。"""

import json
import sys

import httpx

from app.core.config import settings

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    payload = {
        "query": "OEM manufacturer Germany industrial automation",
        "count": 5,
        "need_content": False,
    }
    r = httpx.post(
        "https://api.deepseek.com/v1/tools/search",
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    print("status:", r.status_code)
    if r.status_code != 200:
        print(r.text[:500])
        return
    data = r.json()
    results = data.get("results", [])
    print("结果数:", len(results))
    for item in results:
        print("---")
        print("title:", item.get("title"))
        print("url:", item.get("url"))
        print("rerank:", item.get("rerank_score"), "| authority:", item.get("authority"))
        print("summary:", (item.get("summary") or "")[:120])


if __name__ == "__main__":
    main()
