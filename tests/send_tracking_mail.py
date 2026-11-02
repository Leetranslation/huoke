"""发一封带有效像素的测试邮件（收件人强制为测试邮箱）。"""

import subprocess
import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8001"
TEST_EMAIL = "3793458109@qq.com"


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=120)

    # 找一个还没发过信的联系人（同公司 143 = Airswift）
    contacts = c.get("/contacts").json()
    cands = [x for x in contacts if x["company_id"] == 143 and x["status"] == "pending"]
    if not cands:
        print("没有可用联系人")
        return
    target = cands[0]
    print(f"联系人 id={target['id']} 原邮箱={target['email']}")

    # 改库改邮箱，防误发真实客户
    subprocess.run(
        ["docker", "exec", "yxagent-db", "psql", "-U", "postgres", "-d", "yxagent", "-c",
         f"UPDATE contacts SET email='{TEST_EMAIL}' WHERE id={target['id']};"],
        capture_output=True,
    )

    r = c.post(f"/companies/143/emails", json={"contact_id": target["id"]})
    if r.status_code != 200:
        print("生成失败", r.status_code, r.text[:200])
        return
    e = r.json()
    print(f"草稿 id={e['id']}  主题：{e['subject']}")

    c.post(f"/emails/{e['id']}/submit")
    c.post(f"/emails/{e['id']}/approve")
    r = c.post(f"/emails/{e['id']}/send")
    print("发送：", r.json())

    final = [x for x in c.get("/emails").json() if x["id"] == e["id"]][0]
    print(f"状态={final['status']} 收件人={final['contact_email']}")
    print(f"\n请打开 QQ 邮箱，点开「{e['subject'][:40]}...」，然后告诉我")
    c.close()


if __name__ == "__main__":
    main()
