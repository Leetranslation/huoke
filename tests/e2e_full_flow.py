"""端到端流程：检索客户 → 画像 → 联系人 → 开发信 → 发送到测试邮箱。

安全：生成开发信前，把收件人邮箱强制改成测试邮箱，绝不发给真实客户。
"""

import sys

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8001"
TEST_EMAIL = "3793458109@qq.com"
CAMPAIGN_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 9


def step(msg: str) -> None:
    print(f"\n>>> {msg}")


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=300)

    # 0. 前置检查
    step("0. 读取任务信息")
    camps = c.get("/campaigns").json()
    camp = next((x for x in camps if x["id"] == CAMPAIGN_ID), None)
    if not camp:
        print(f"任务 {CAMPAIGN_ID} 不存在")
        return
    print(f"任务：{camp['name']} | 产品：{camp['product_name']} | 官网：{camp['website'] or '-'}")
    print(f"DNA：{'已有' if camp.get('dna') else '无'}")

    # 1. DNA
    if not camp.get("dna"):
        step("1. AI 分析官网（约 0.01 元）")
        r = c.post(f"/campaigns/{CAMPAIGN_ID}/analyze-dna")
        if r.status_code != 200:
            print("失败:", r.status_code, r.text[:200])
            return
        dna = r.json()
        print(f"产品：{dna.get('product_name')} | 客户类型：{len(dna.get('customer_types') or [])} 类")
    else:
        print("→ DNA 已存在，跳过分析")

    # 2. 爬取线索
    step("2. 爬取线索（Tavily + LLM 实体抽取，每类 2 家，约 0.03-0.05 元）")
    r = c.post(f"/campaigns/{CAMPAIGN_ID}/crawl", params={"count": 2, "source": "tavily"})
    if r.status_code != 200:
        print("失败:", r.status_code, r.text[:300])
        return
    crawled = r.json()
    print(f"新增 {len(crawled)} 家企业")
    for x in crawled[:5]:
        print(f"  - {x['name']} | {x.get('country')} | {x.get('identity')}")

    # 3. 画像
    step("3. AI 画像评分（约 0.05 元）")
    r = c.post(f"/campaigns/{CAMPAIGN_ID}/profile")
    print(f"status={r.status_code}")
    companies = c.get(f"/campaigns/{CAMPAIGN_ID}/companies").json()
    profiled = [x for x in companies if x.get("profile")]
    print(f"已画像 {len(profiled)} / {len(companies)} 家")
    for x in profiled[:3]:
        print(f"  - {x['name']} | {x['match_score']} 分 | {x.get('identity')}")

    # 4. 提取联系人
    step("4. 提取联系人（约 0.03 元）")
    r = c.post(f"/campaigns/{CAMPAIGN_ID}/extract-contacts")
    print(f"status={r.status_code} {r.text[:150]}")

    all_contacts = c.get("/contacts").json()
    ids = {x["id"] for x in companies}
    mine = [x for x in all_contacts if x["company_id"] in ids]
    print(f"本条任务联系人：{len(mine)} 位")
    for x in mine[:5]:
        print(f"  - {x['name']} | {x['email']} | {x['status']}")

    if not mine:
        print("\n没有联系人，流程中断")
        return

    # 5. 生成开发信（先选一个联系人，改邮箱为测试邮箱）
    step("5. 生成开发信（1 封，约 0.01 元）")
    target = mine[0]
    orig_email = target["email"]
    print(f"原收件人：{orig_email} → 强制改为测试邮箱 {TEST_EMAIL}")

    # 直接改库（避免误发真实客户）
    import subprocess

    sql = f"UPDATE contacts SET email='{TEST_EMAIL}' WHERE id={target['id']};"
    subprocess.run(
        ["docker", "exec", "yxagent-db", "psql", "-U", "postgres", "-d", "yxagent", "-c", sql],
        capture_output=True,
    )

    r = c.post(f"/companies/{target['company_id']}/emails", json={"contact_id": target["id"]})
    if r.status_code != 200:
        print("生成失败:", r.status_code, r.text[:300])
        return
    email = r.json()
    print(f"已生成草稿 id={email['id']}")
    print(f"主题：{email['subject']}")
    print(f"正文前 150 字：{email['body'][:150]}...")

    # 6. 审核 → 批准 → 发送
    step("6. 提交审核")
    r = c.post(f"/emails/{email['id']}/submit")
    print(f"status={r.status_code} {r.text[:100]}")

    step("7. 批准")
    r = c.post(f"/emails/{email['id']}/approve")
    print(f"status={r.status_code} {r.text[:100]}")

    step("8. 发送（真实 SMTP → 测试邮箱）")
    r = c.post(f"/emails/{email['id']}/send")
    print(f"status={r.status_code} {r.text[:200]}")

    # 7. 结果
    step("9. 结果核对")
    final = c.get("/emails").json()
    e = next((x for x in final if x["id"] == email["id"]), None)
    if e:
        print(f"邮件 {e['id']} 状态={e['status']} 收件人={e['contact_email']}")
        print(f"打开={e['open_count']} 点击={e['click_count']}")
        if e["status"] == "sent":
            print("\n✅ 全链路通过：检索 → 画像 → 联系人 → 开发信 → 发送")
            print(f"   请打开 QQ 邮箱 {TEST_EMAIL} 查收，然后回来自动/手动查追踪")
        else:
            print(f"\n⚠️ 最终状态为 {e['status']}，查看发送失败原因")

    c.close()


if __name__ == "__main__":
    main()
