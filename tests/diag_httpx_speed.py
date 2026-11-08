"""对比：httpx 直抓 vs DeepSeekFetch，看速度与邮箱命中率。"""

import asyncio
import re
import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
EXCLUDE = ("noreply", "no-reply", "example.", "sentry", "your-email", "yourname", "@2x", ".png", ".jpg", ".svg")

URLS = [
    "https://www.maximator.de/",
    "https://www.lhyfe.com/",
    "https://www.schaeffler.com/",
    "https://www.stauff.com/",
]


async def grab(client: httpx.AsyncClient, url: str) -> tuple[float, int, list[str]]:
    t = time.time()
    try:
        r = await client.get(url, timeout=8, follow_redirects=True)
        cost = time.time() - t
        html = r.text or ""
        emails = []
        for e in EMAIL_RE.findall(html):
            low = e.lower()
            if any(x in low for x in EXCLUDE) or len(e) > 100:
                continue
            if e not in emails:
                emails.append(e)
        return cost, r.status_code, emails[:3]
    except Exception as ex:  # noqa: BLE001
        return time.time() - t, 0, [f"ERR:{type(ex).__name__}"]


async def main() -> None:
    print("=== httpx 直抓（并发 3 页/家）===")
    async with httpx.AsyncClient(headers={"User-Agent": UA}) as client:
        for base in URLS:
            b = base.rstrip("/")
            pages = [b, b + "/contact", b + "/about"]
            t = time.time()
            results = await asyncio.gather(*[grab(client, u) for u in pages])
            total = time.time() - t
            allmails = []
            for _, code, mails in results:
                for m in mails:
                    if not m.startswith("ERR") and m not in allmails:
                        allmails.append(m)
            codes = [c for _, c, _ in results]
            print(f"  {base:35} → {total:.1f}s | 状态 {codes} | {len(allmails)} 邮箱 {allmails[:2]}")


if __name__ == "__main__":
    asyncio.run(main())
