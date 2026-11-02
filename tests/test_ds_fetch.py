"""测试 DeepSeek Fetch API 返回结构。"""

import sys

import httpx

from app.core.config import settings

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    r = httpx.post(
        "https://api.deepseek.com/v1/tools/fetch",
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        json={"url": "https://www.maximator.de/en/homepage-2123464850.html"},
        timeout=30,
    )
    print("status:", r.status_code)
    print("body 前 1500 字:")
    print(r.text[:1500])


if __name__ == "__main__":
    main()
