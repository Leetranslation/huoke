"""诊断：用 TestClient 走完整 HTTP 链路，抓 500 的真实异常。"""

import sys
import time
import traceback

from fastapi.testclient import TestClient

from app.main import app

sys.stdout.reconfigure(encoding="utf-8")

COMPANY_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 151
CONTACT_ID = int(sys.argv[2]) if len(sys.argv) > 2 else 92


def main() -> None:
    # raise_server_exceptions=True：把服务端异常直接抛出来，而不是转成 500
    client = TestClient(app, raise_server_exceptions=True)
    t = time.time()
    try:
        r = client.post(
            f"/companies/{COMPANY_ID}/emails", json={"contact_id": CONTACT_ID}
        )
        print(f"耗时 {time.time()-t:.1f}s | status={r.status_code}")
        print(r.text[:300])
    except Exception:  # noqa: BLE001
        print(f"耗时 {time.time()-t:.1f}s | 抛出异常：")
        traceback.print_exc()


if __name__ == "__main__":
    main()
