"""Europages 数据源：爬取 B2B 目录站的真实公司线索。

流程：行业搜索页 → 收集公司主页链接 → 逐个访问主页 → 提取公司名/国家/官网。
注意：需设置 PLAYWRIGHT_NODEJS_PATH 指向系统 node（本机 Playwright 内置 node 有兼容问题）。
"""

import os
import re
from urllib.parse import quote

os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", r"C:\Program Files\nodejs\node.exe")

from playwright.sync_api import sync_playwright  # noqa: E402

from app.datasources.base import CompanyRaw, DataSource  # noqa: E402

BASE = "https://www.europages.co.uk"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

COUNTRIES = [
    "Spain", "France", "Germany", "Italy", "Turkey", "Netherlands", "Belgium",
    "Poland", "Portugal", "Sweden", "Norway", "Denmark", "Finland", "Austria",
    "Switzerland", "Czech Republic", "Greece", "United Kingdom", "Ireland",
    "United States", "Canada", "Australia", "Japan", "South Korea", "China",
    "India", "Brazil", "Mexico", "United Arab Emirates", "Saudi Arabia",
    "Egypt", "Morocco", "Tunisia", "Hungary", "Romania", "Bulgaria",
]


class EuropagesDataSource(DataSource):
    """从 Europages 行业页爬取公司线索（公司名、国家、官网、行业）。"""

    def __init__(self, query: str, max_companies: int = 10):
        self._query = query
        self._max = max_companies

    def fetch(self) -> list[CompanyRaw]:
        results: list[CompanyRaw] = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, channel="chromium")
            page = browser.new_page(user_agent=UA)
            page.goto(f"{BASE}/companies/{quote(self._query)}.html", timeout=60000)
            page.wait_for_timeout(3000)

            hrefs: list[str] = []
            for a in page.query_selector_all("a[href*='/en/company/']"):
                href = a.get_attribute("href") or ""
                m = re.match(r"(/en/company/[a-z0-9-]+-\d+)/?$", href)
                if m and m.group(1) not in hrefs:
                    hrefs.append(m.group(1))

            for href in hrefs[: self._max]:
                try:
                    page.goto(BASE + href, timeout=60000)
                    page.wait_for_timeout(2000)
                    results.append(self._parse(page))
                except Exception:  # noqa: BLE001
                    continue

            browser.close()
        return results

    def _parse(self, page) -> CompanyRaw:
        title = page.title()
        name = title.split(" in ")[0].strip() if " in " in title else title
        body = page.inner_text("body")

        country = ""
        head = body[:1500]
        for c in COUNTRIES:
            if c in head:
                country = c
                break

        website = ""
        for a in page.query_selector_all("a[href^='http']"):
            h = a.get_attribute("href") or ""
            if not any(
                x in h
                for x in ("europages", "google", "visable", "cookie-script")
            ):
                website = h
                break

        # 业务描述：Delivery area 之后到 Read more / Contact supplier 之前
        description = ""
        m = re.search(
            r"Delivery area:[^\n]*\n(.+?)(?:\nRead more|\nContact supplier)",
            body,
            re.S,
        )
        if m:
            description = m.group(1).strip()
        if not description:
            meta = page.query_selector('meta[name="description"]')
            if meta:
                description = (meta.get_attribute("content") or "").strip()

        return CompanyRaw(
            name=name,
            website=website,
            country=country,
            industry=self._query,
            description=description[:2000],
            source="europages",
        )
