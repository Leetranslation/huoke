"""验证跟进看板接口（公司名 + 上次扫描）。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    r = httpx.get("http://127.0.0.1:8001/contacts", timeout=15)
    print("contacts:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print(f"  共 {len(data)} 个")
        for c in data[:4]:
            print(
                f"  [{c['status']}] {c['name']} | {c['title']} | {c['email']} | "
                f"公司={c.get('company_name') or '(空)'}"
            )

    r2 = httpx.get("http://127.0.0.1:8001/followup/last-scan", timeout=15)
    print("last-scan:", r2.status_code, r2.json())


if __name__ == "__main__":
    main()
