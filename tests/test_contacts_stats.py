"""验证联系人统计接口。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    r = httpx.get("http://127.0.0.1:8001/contacts", timeout=20)
    print("status:", r.status_code)
    if r.status_code != 200:
        print(r.text[:300])
        return
    data = r.json()
    print(f"共 {len(data)} 个联系人")
    for c in data[:6]:
        print(
            f"[{c['status']}] {c['name']} | {c.get('company_name') or '-'} | "
            f"open={c['open_count']} click={c['click_count']} | last={c.get('last_sent_at') or '-'}"
        )


if __name__ == "__main__":
    main()
