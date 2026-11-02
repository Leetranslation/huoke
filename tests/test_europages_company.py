"""测试 Europages 公司主页：提取公司名、国家、官网。"""

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
            "https://www.europages.co.uk/en/company/venalsol-smart-light-sl-20700885/",
            timeout=60000,
        )
        page.wait_for_timeout(4000)
        print("标题:", page.title())
        print("URL:", page.url)
        body = page.inner_text("body")
        print("正文前 600 字:", body[:600].replace("\n", " | "))

        print("\n=== 外部链接（官网候选）===")
        links = page.query_selector_all("a[href^='http']")
        for a in links:
            href = a.get_attribute("href") or ""
            if "europages" not in href and "google" not in href:
                print(" -", href[:100])

        browser.close()


if __name__ == "__main__":
    main()
