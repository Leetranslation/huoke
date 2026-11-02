"""Tavily 搜索数据源：AI 优化的搜索引擎，返回干净的网页结果。

相比 DeepSeek Search，Tavily 支持 exclude_domains，能直接排掉新闻站/情报站，
返回结果多为真实公司官网。
"""

import logging
import re

import httpx

from app.core.config import settings
from app.datasources.base import CompanyRaw, DataSource

logger = logging.getLogger(__name__)

TAVILY_URL = "https://api.tavily.com/search"

# 搜索时直接排除的域名（新闻/情报站/社交/百科/招聘/电商）
EXCLUDE_DOMAINS = [
    # 新闻媒体
    "yahoo.com", "cnbc.com", "bbc.com", "bbc.co.uk", "reuters.com", "forbes.com",
    "bloomberg.com", "ft.com", "wsj.com", "nytimes.com", "cnn.com", "theguardian.com",
    # 公司情报 / 数据库
    "tracxn.com", "crunchbase.com", "cbinsights.com", "zoominfo.com", "pitchbook.com",
    "owler.com", "dnb.com", "apollo.io", "growjo.com", "leadiq.com",
    # 金融 / 股票
    "investing.com", "marketscreener.com", "morningstar.com", "finance.yahoo.com",
    "nasdaq.com", "marketwatch.com",
    # 社交 / 百科
    "linkedin.com", "wikipedia.org", "youtube.com", "facebook.com", "twitter.com",
    "x.com", "instagram.com", "xing.com", "reddit.com", "quora.com",
    # 招聘
    "indeed.com", "glassdoor.com", "simplify.jobs", "myworkdayjobs.com", "careers.",
    # 电商 / 平台
    "amazon.com", "alibaba.com", "made-in-china.com", "globalsources.com",
    "ebay.com", "etsy.com", "walmart.com",
    # B2B 目录站
    "chemeurope.com", "europages.com", "europages.co.uk", "ensun.io", "kompass.com",
    "europages.de", "wlw.de", "industrystock.com", "directindustry.com",
    # 行业媒体 / 知识库
    "mobilehydraulictips.com", "hyfindr.com", "pv-magazine.com", "eenewspower.com",
    "hydraulicspneumatics.com", "processingmagazine.com",
    # 公关稿
    "prnewswire.com", "businesswire.com", "globenewswire.com", "einpresswire.com",
]

# 标题不像公司名的词（网页标题噪声）
BAD_TITLE = (
    "what is", "what are", "how to", "guide", "top 10", "top 100", "best ",
    "list of", "directory", "catalog", "catalogue", "marketplace", "suppliers",
    "supplier directory", "find ", "wikipedia", "definition", "explained",
    "home", "about us", "contact us", "products", "product ", "services",
    "solutions", "news", "press", "report", "market size", "overview",
    "inaugurates", "announces", "opens", "appoints", "launches", "acquires",
    "completes", "partners", "invests", "expands", "receives",
)

CJK_RE = re.compile(r"[\u4e00-\u9fff]")

# 标题里的栏目/页面噪声词 → 该标题不是公司名
PAGE_NOISE = (
    "map", "companies", "company list", "facilities", "facility", "laboratory",
    "lab ", "test ", "services", "products", "product", "solutions", "list",
    "directory", "station", "stations", "home", "about", "contact", "overview",
    "profile", "welcome", "portal", "search result",
)

# 国家顶级域名（用于剥离域名得到公司名）
TLDS = {
    "com", "de", "co.uk", "uk", "fr", "it", "es", "nl", "be", "at", "ch", "se",
    "no", "dk", "fi", "pl", "cz", "pt", "ie", "eu", "org", "net", "io", "co",
}


def _name_from_url(url: str) -> str:
    """从域名推断公司名：https://www.enbw.com/xxx → Enbw"""
    host = (url or "").split("//")[-1].split("/")[0].lower()
    host = host.replace("www.", "").replace("www2.", "")
    parts = host.split(".")
    if len(parts) < 2:
        return ""
    # 去掉 TLD（两段的情况，如 co.uk）
    core = parts[0]
    if len(parts) >= 3 and f"{parts[-2]}.{parts[-1]}" in TLDS:
        core = parts[-3]
    elif parts[-1] in TLDS:
        core = parts[-2]
    core = core.replace("-", " ").strip()
    return core.title() if core else ""


def _pick_name(title: str, url: str) -> str:
    """优先用标题，标题像栏目页时回退到域名。"""
    t = (title or "").strip()
    for sep in (" | ", " - ", " — ", " – "):
        t = t.split(sep)[0].strip()

    low = t.lower()
    looks_like_page = (
        len(t) < 4
        or len(t) > 40
        or any(w in low for w in PAGE_NOISE)
        or low.endswith(("companies", "solutions", "services", "products"))
    )
    if looks_like_page:
        from_url = _name_from_url(url)
        return from_url or t
    return t


class TavilyDataSource(DataSource):
    """用 Tavily 搜索发现目标公司。"""

    def __init__(self, query: str, count: int = 8):
        self._query = query
        self._count = max(1, min(count * 2, 20))  # 多取一些，过滤后留够
        self.raw_results: list[dict] = []  # 保留原始结果，供 LLM 实体抽取用

    def fetch(self) -> list[CompanyRaw]:
        if not settings.tavily_api_key:
            logger.warning("未配置 TAVILY_API_KEY")
            return []

        try:
            r = httpx.post(
                TAVILY_URL,
                headers={
                    "Authorization": f"Bearer {settings.tavily_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": self._query,
                    "max_results": self._count,
                    "search_depth": "basic",
                    "exclude_domains": EXCLUDE_DOMAINS,
                },
                timeout=45,
            )
            if r.status_code != 200:
                logger.warning("Tavily %s: %s", r.status_code, r.text[:200])
                return []
            results = r.json().get("results", [])
            self.raw_results = results
        except Exception as e:  # noqa: BLE001
            logger.warning("Tavily 请求失败: %s", e)
            return []

        english = not CJK_RE.search(self._query)
        companies: list[CompanyRaw] = []
        seen: set[str] = set()

        for item in results:
            url = (item.get("url") or "").strip()
            if not url:
                continue
            low_url = url.lower()

            # 路径过滤（新闻/博客/知识库/产品详情）
            if any(p in low_url for p in ("/news/", "/blog/", "/press/", "/knowledge/", "/wiki/", "/insight")):
                continue

            name = _pick_name(item.get("title") or "", url)

            if not name or len(name) < 3 or len(name) > 40:
                continue
            if english and CJK_RE.search(name):
                continue

            low_name = name.lower()
            if any(x in low_name for x in BAD_TITLE):
                continue

            key = low_url.rstrip("/")
            if key in seen:
                continue
            seen.add(key)

            companies.append(
                CompanyRaw(
                    name=name,
                    website=url,
                    country="",
                    industry=self._query,
                    description=(item.get("content") or "")[:1000],
                    source="tavily",
                )
            )

        return companies
