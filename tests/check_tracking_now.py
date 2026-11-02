"""检查邮件 15 的追踪 + 拉取新回复。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8001"


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=180)

    e = [x for x in c.get("/emails").json() if x["id"] == 15]
    if e:
        e = e[0]
        print(f"邮件15: 状态={e['status']} 打开={e['open_count']} 点击={e['click_count']}")

    print("\n拉取新回复...")
    from app.tasks.followup import check_replies

    print("结果:", check_replies())

    print("\n当前所有已回复联系人：")
    for x in c.get("/contacts").json():
        if x.get("last_reply_subject"):
            print(f"  id={x['id']} {x['email']} | {x['status']} | {x['last_reply_subject'][:50]}")

    c.close()


if __name__ == "__main__":
    main()
