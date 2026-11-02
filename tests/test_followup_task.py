"""测试定时跟进任务（手动触发一次）。"""

import sys

from app.tasks.followup import daily_scan

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    result = daily_scan()
    print("扫描结果:", result)


if __name__ == "__main__":
    main()
