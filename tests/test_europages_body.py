"""探索 Europages 公司主页正文结构，定位业务描述位置。"""

import re
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="chromium")
    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
    )
    page.goto(
        "https://www.europages.co.uk/companies/manufacturer%20germany.html",
        timeout=60000,
    )
    page.wait_for_timeout(3000)

    href = None
    for a in page.query_selector_all("a[href*='/en/company/']"):
        h = a.get_attribute("href") or ""
        m = re.match(r"(/en/company/[a-z0-9-]+-\d+)/?$", h)
        if m:
            href = m.group(1)
            break

    print("公司 URL:", href)
    page.goto("https://www.europages.co.uk" + (href or ""), timeout=60000)
    page.wait_for_timeout(3000)
    body = page.inner_text("body")
    print("=== body 前 2000 字 ===")
    print(body[:2000])

    browser.close()
