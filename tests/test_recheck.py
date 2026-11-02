"""触发收信检查并查看回复。"""

import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    r = httpx.post("http://127.0.0.1:8001/followup/check-replies", timeout=30)
    print("trigger:", r.json())
    time.sleep(6)
    r2 = httpx.get("http://127.0.0.1:8001/contacts", timeout=30)
    for c in r2.json():
        if c.get("last_reply_subject"):
            print(f"[{c['status']}] {c['name']} | {c.get('company_name')} | {c.get('last_reply_subject')[:50]}")


if __name__ == "__main__":
    main()
