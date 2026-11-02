"""测试收信检查：触发 check_replies，验证测试客户变 replied。"""

import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    r = httpx.post("http://127.0.0.1:8001/followup/check-replies", timeout=30)
    print("check-replies:", r.status_code, r.text[:120])

    time.sleep(8)

    r2 = httpx.get("http://127.0.0.1:8001/contacts", timeout=30)
    for c in r2.json():
        if c.get("status") == "replied" or c.get("last_reply_subject"):
            print(
                f"[{c['status']}] {c['name']} | {c.get('company_name') or '-'} | "
                f"回复: {c.get('last_reply_subject') or '-'}"
            )


if __name__ == "__main__":
    main()
