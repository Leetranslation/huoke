"""功能回归测试：验证 UI 改版后接口与主流程是否正常（不发送真实邮件）。"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8001"
ok = 0
fail = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global ok, fail
    if cond:
        ok += 1
        print(f"PASS | {name} {detail}")
    else:
        fail += 1
        print(f"FAIL | {name} {detail}")


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=30)

    # ---- 1. 健康检查 ----
    r = c.get("/health")
    check("健康检查", r.status_code == 200, r.text)

    # ---- 2. 各列表接口 ----
    camps = c.get("/campaigns").json()
    check("任务列表", isinstance(camps, list) and len(camps) > 0, f"{len(camps)} 条")

    companies = c.get("/companies").json()
    check("公司列表", isinstance(companies, list) and len(companies) > 0, f"{len(companies)} 家")

    contacts = c.get("/contacts").json()
    check("联系人列表", isinstance(contacts, list), f"{len(contacts)} 位")

    has_stats = all(
        k in contacts[0] for k in ("open_count", "click_count", "company_name")
    ) if contacts else False
    check("联系人统计字段", has_stats, "open_count/click_count/company_name 都在")

    emails = c.get("/emails").json()
    check("邮件列表", isinstance(emails, list), f"{len(emails)} 封")

    ls = c.get("/followup/last-scan").json()
    check("上次扫描时间", "last_scan" in ls, str(ls.get("last_scan")))

    # ---- 3. 公司详情 + 回复 ----
    if companies:
        cid = companies[0]["id"]
        r = c.get(f"/companies/{cid}")
        check("公司详情", r.status_code == 200 and r.json().get("id") == cid)
        r = c.get(f"/companies/{cid}/replies")
        check("公司回复接口", r.status_code == 200 and isinstance(r.json(), list), f"{len(r.json())} 封")

    # ---- 4. 创建任务（新表单字段）----
    payload = {
        "name": "【回归测试】UI 改版验证任务",
        "product_name": "test product",
        "website": "https://example.com",
        "target_market": ["北美", "西欧"],
        "keywords": ["区域总代", "分销商"],
    }
    r = c.post("/campaigns", json=payload)
    created = r.status_code == 200
    check("创建任务（target_market/keywords 数组）", created, f"status={r.status_code}")
    new_id = None
    if created:
        d = r.json()
        new_id = d["id"]
        check("任务字段落库", d.get("target_market") == ["北美", "西欧"] and d.get("keywords") == ["区域总代", "分销商"],
              f"market={d.get('target_market')} keywords={d.get('keywords')}")

    # ---- 5. 邮件编辑接口（草稿可编辑 / 已发送拒绝）----
    drafts = [e for e in emails if e["status"] == "draft"]
    if drafts:
        r = c.patch(f"/emails/{drafts[0]['id']}", json={"subject": drafts[0]["subject"]})
        check("草稿可编辑", r.status_code == 200)
    sents = [e for e in emails if e["status"] == "sent"]
    if sents:
        r = c.patch(f"/emails/{sents[0]['id']}", json={"subject": "x"})
        check("已发送拒绝编辑", r.status_code == 400, str(r.status_code))

    # ---- 6. 跟进扫描任务投递（不等待执行）----
    r = c.post("/followup/run")
    check("跟进扫描任务投递", r.status_code == 200 and "task_id" in r.json())
    r = c.post("/followup/check-replies")
    check("收信任务投递", r.status_code == 200 and "task_id" in r.json())

    print(f"\n{'=' * 50}\n通过 {ok} / {ok + fail}")
    if new_id:
        print(f"测试任务 id={new_id}（可在 UI 里手动删除，或留作演示）")
    c.close()


if __name__ == "__main__":
    main()
