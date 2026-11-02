"""M7 API 冒烟测试：TestClient 走通「建任务 → 导入 → 客户池列表」。"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def main() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    print("health:", r.json())

    r = client.post("/campaigns", json={"name": "api test", "product_name": "LED light"})
    assert r.status_code == 200
    cid = r.json()["id"]
    print("create campaign id:", cid)

    r = client.post(f"/campaigns/{cid}/import")
    assert r.status_code == 200
    print("import companies:", len(r.json()))

    r = client.get(f"/campaigns/{cid}/companies")
    assert r.status_code == 200
    print("list companies:", len(r.json()))

    print("API SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
