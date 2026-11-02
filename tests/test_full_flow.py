"""完整闭环测试：建任务 → DNA → 同行客户 → 画像 → 联系人 → 开发信。"""

import asyncio
import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8001"


async def main() -> None:
    async with httpx.AsyncClient(timeout=900) as c:
        t0 = time.time()

        # 1. 创建任务
        r = await c.post(
            f"{BASE}/campaigns",
            json={
                "name": "高压设备",
                "product_name": "高压设备（液压/气动元件）",
                "website": "https://www.maximator.de/",
                "target_market": ["United States"],
            },
        )
        if r.status_code not in (200, 201):
            print("创建失败:", r.status_code, r.text[:300])
            return
        cid = r.json()["id"]
        print(f"[1] 创建任务 id={cid}")

        # 2. 企业 DNA
        r = await c.post(f"{BASE}/campaigns/{cid}/analyze-dna")
        print(f"[2] DNA: {r.status_code}")
        if r.status_code == 200:
            dna = r.json()
            print("    产品:", dna.get("product_name"))
            names = [
                t.get("name") if isinstance(t, dict) else t
                for t in dna.get("customer_types", [])
            ]
            print("    客户类型:", names)
            print("    排除规则:", dna.get("exclude_rules"))

        # 3. 同行客户
        r = await c.post(
            f"{BASE}/campaigns/{cid}/crawl-competitor-customers",
            params={"competitor": "maximator", "max_rows": 13},
        )
        print(f"[3] 同行客户: {r.status_code}")
        if r.status_code == 200:
            print(f"    拿到 {len(r.json())} 个买家")
        else:
            print("   ", r.text[:300])

        # 4. 画像
        r = await c.post(f"{BASE}/campaigns/{cid}/profile")
        print(f"[4] 画像: {r.status_code}")
        ranked = []
        if r.status_code == 200:
            ranked = sorted(r.json(), key=lambda x: -(x.get("match_score") or 0))
            for co in ranked[:5]:
                print(f"    {co['match_score']} 分 [{co['identity']}] {co['name']}")

        # 5. 提取联系人
        r = await c.post(f"{BASE}/campaigns/{cid}/extract-contacts")
        print(f"[5] 联系人: {r.status_code} {r.json() if r.status_code == 200 else r.text[:200]}")

        # 6. 生成开发信（第一家）
        if ranked:
            target = ranked[0]
            rr = await c.get(f"{BASE}/companies/{target['id']}")
            company = rr.json()
            contacts = company.get("contacts") or []
            print(f"[6] 目标公司: {target['name']} | 联系人 {len(contacts)} 个")
            if contacts:
                contact = contacts[0]
                r = await c.post(
                    f"{BASE}/companies/{target['id']}/emails",
                    json={"contact_id": contact["id"]},
                )
                print(f"    开发信: {r.status_code}")
                if r.status_code == 200:
                    email = r.json()
                    print("    主题:", email.get("subject"))
                    print("    正文:\n", (email.get("body") or "")[:800])
        
        print(f"\n总耗时: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
