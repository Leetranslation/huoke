"""Google 爬虫可行性验证：Playwright 打开 Google 搜索，抓取结果链接。"""

from urllib.parse import quote

from playwright.sync_api import sync_playwright


def main() -> None:
    query = "LED light buyer distributor Germany"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chromium")
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
        )
        page.goto(
            f"https://www.google.com/search?q={quote(query)}&hl=en",
            timeout=60000,
        )
        page.wait_for_timeout(3000)
        print("页面标题:", page.title())
        print("当前 URL:", page.url)

        # 抓取结果标题（h3 包在 a 里）
        links = page.query_selector_all("a h3")
        print("结果数:", len(links))
        for i, h3 in enumerate(links[:10]):
            a = h3.evaluate_handle("el => el.closest('a')")
            href = a.get_attribute("href") if a else ""
            print(f"{i + 1}. {h3.inner_text()} | {href}")

        browser.close()


if __name__ == "__main__":
    main()
