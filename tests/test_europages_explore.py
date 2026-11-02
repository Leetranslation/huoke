"""探索 Europages 公司卡片结构，确认提取选择器。"""

import re

from playwright.sync_api import sync_playwright


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chromium")
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
        )
        page.goto(
            "https://www.europages.co.uk/companies/led%20lighting.html",
            timeout=60000,
        )
        page.wait_for_timeout(4000)

        cards = page.query_selector_all("a[href*='/en/company/']")
        seen: dict[str, str] = {}
        for a in cards:
            href = a.get_attribute("href") or ""
            m = re.search(r"/en/company/([a-z0-9-]+)-\d+/", href)
            if not m:
                continue
            slug = m.group(1)
            if slug in seen:
                continue
            txt = a.evaluate(
                "el => { let n=el; for(let i=0;i<6;i++){ if(n.parentElement && "
                "n.parentElement.innerText.length>60) return n.parentElement.innerText; "
                "n=n.parentElement;} return ''; }"
            )
            seen[slug] = txt or ""

        print("唯一公司数:", len(seen))
        for slug, txt in list(seen.items())[:8]:
            print("=" * 40)
            print("slug:", slug)
            print("文本:", txt[:220].replace("\n", " | "))

        browser.close()


if __name__ == "__main__":
    main()
