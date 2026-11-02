"""Europages 爬虫可行性验证：打开目录站，看是否可访问、能否拿到公司数据。"""

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

        # 1. 测试首页
        print("=== 打开 Europages 首页 ===")
        page.goto("https://www.europages.co.uk/", timeout=60000)
        page.wait_for_timeout(3000)
        print("标题:", page.title())
        print("URL:", page.url)
        text = page.inner_text("body")
        print("正文前 300 字:", text[:300].replace("\n", " "))

        # 2. 测试搜索页
        print("\n=== 打开行业搜索页 ===")
        page.goto(
            "https://www.europages.co.uk/companies/led%20lighting.html",
            timeout=60000,
        )
        page.wait_for_timeout(3000)
        print("标题:", page.title())
        print("URL:", page.url)
        t2 = page.inner_text("body")
        print("正文前 400 字:", t2[:400].replace("\n", " "))

        # 3. 尝试抓公司卡片链接
        cards = page.query_selector_all("a[href*='company']")
        print("\n公司链接候选数:", len(cards))
        for a in cards[:10]:
            print(" -", a.inner_text().strip()[:40], "|", a.get_attribute("href"))

        browser.close()


if __name__ == "__main__":
    main()
