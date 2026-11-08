"""诊断：直接调生成开发信的 API，定位耗时与失败原因。"""

import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8001"
COMPANY_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 151


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=200)

    # 取该公司的联系人
    contacts = [x for x in c.get("/contacts").json() if x["company_id"] == COMPANY_ID]
    print(f"公司 {COMPANY_ID} 有 {len(contacts)} 位联系人")
    for x in contacts:
        print(f"  id={x['id']} {x['name']} | {x['email']} | {x['status']}")

    if len(contacts) < 2:
        print("联系人数不足 2，无法复现并发场景")
        return

    # 看该公司的 profile 大小（prompt 体积来源）
    co = c.get(f"/companies/{COMPANY_ID}").json()
    prof = co.get("profile") or {}
    print(f"\nprofile 字段: {list(prof.keys())}")
    for k, v in prof.items():
        print(f"  {k}: {len(str(v))} 字符")
    print(f"profile 总计: {len(str(prof))} 字符")

    # 顺序两次，记录耗时
    print("\n=== 顺序生成（联系人1）===")
    t = time.time()
    try:
        r = c.post(f"/companies/{COMPANY_ID}/emails", json={"contact_id": contacts[0]["id"]})
        print(f"耗时 {time.time()-t:.1f}s | status={r.status_code} | {r.text[:150]}")
    except Exception as e:  # noqa: BLE001
        print(f"耗时 {time.time()-t:.1f}s | 异常 {type(e).__name__}: {e}")

    print("\n=== 顺序生成（联系人2）===")
    t = time.time()
    try:
        r = c.post(f"/companies/{COMPANY_ID}/emails", json={"contact_id": contacts[1]["id"]})
        print(f"耗时 {time.time()-t:.1f}s | status={r.status_code} | {r.text[:200]}")
    except Exception as e:  # noqa: BLE001
        print(f"耗时 {time.time()-t:.1f}s | 异常 {type(e).__name__}: {e}")

    c.close()


if __name__ == "__main__":
    main()
