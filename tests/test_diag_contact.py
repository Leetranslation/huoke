"""诊断官网访问与邮箱提取。"""

import re
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

SITES = [
    "http://www.steinfels-swiss.ch/",
    "http://www.medigruen.com",
    "http://www.bwf-profiles.de/",
    "http://www.rcp-ranstadt.com/",
    "http://www.k-ley.de/",
]

for url in SITES:
    try:
        r = httpx.get(url, headers={"User-Agent": UA}, timeout=12, follow_redirects=True)
        emails = EMAIL_RE.findall(r.text or "")
        print(f"{url} | status={r.status_code} | len={len(r.text or '')} | emails={emails[:5]}")
    except Exception as e:  # noqa: BLE001
        print(f"{url} | ERROR: {type(e).__name__}: {e}")
