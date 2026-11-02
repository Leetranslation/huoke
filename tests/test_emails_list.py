"""验证邮件列表返回追踪数据。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    r = httpx.get("http://127.0.0.1:8001/emails", timeout=15)
    print("status:", r.status_code)
    if r.status_code != 200:
        print(r.text[:400])
        return
    for e in r.json():
        print(
            f"id={e['id']} | {e['subject'][:26]} | {e['company_name']} | "
            f"{e['contact_email']} | open={e['open_count']} click={e['click_count']} | {e['status']}"
        )


if __name__ == "__main__":
    main()
