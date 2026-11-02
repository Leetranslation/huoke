"""DeepSeek Search 数据源：官方搜索 API 发现公司（无反爬，0.005 元/次）。"""

import re

import httpx

from app.core.config import settings
from app.datasources.base import CompanyRaw, DataSource

SEARCH_URL = "https://api.deepseek.com/v1/tools/search"

# 排除非公司页面（社交/百科/法律/新闻/平台/应用商店/情报站/媒体）
EXCLUDE_DOMAINS = (
    "linkedin.com",
    "wikipedia.org",
    "baike.baidu.com",
    "zhihu.com",
    "youtube.com",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "xing.com",
    "indeed.com",
    "glassdoor.com",
    "techtarget.com",
    "westlaw.com",
    "law.cornell.edu",
    "britannica.com",
    "investopedia.com",
    "medium.com",
    "reddit.com",
    "quora.com",
    "sohu.com",
    "163.com",
    "sina.com",
    # 平台/电商/应用商店（不是公司官网）
    "alibaba.com",
    "made-in-china.com",
    "globalsources.com",
    "apps.apple.com",
    "play.google.com",
    "amazon.com",
    "ebay.com",
    "etsy.com",
    "walmart.com",
    # 公司情报站 / 数据库（不是目标公司官网）
    "cbinsights.com",
    "crunchbase.com",
    "bloomberg.com",
    "zoominfo.com",
    "dnb.com",
    "pitchbook.com",
    "owler.com",
    "apollo.io",
    "chemxplore.com",
    "interactanalysis.com",
    "marketsandmarkets.com",
    "grandviewresearch.com",
    "statista.com",
    # 媒体 / 新闻 / 地方报
    "szdaily.com",
    "reuters.com",
    "forbes.com",
    "cnbc.com",
    "prnewswire.com",
    "businesswire.com",
    "globenewswire.com",
    "eenewspower.com",
    "pv-magazine.com",
    "offshore-energy.biz",
    # 中国无关站点（理财/资讯/聚合）
    "alipay.com",
    "render.alipay.com",
    "toutiao.com",
    "baijiahao.baidu.com",
    "163.com",
    "qq.com",
    "ifeng.com",
    "eastmoney.com",
    # 展会 / 目录 / 市场平台
    "exaexpo.com.au",
    "eiturbanmobility.eu",
    "marketplace.",
    "europages.co.uk",
)

# 排除内容页路径（博客/新闻/文章）
EXCLUDE_PATH = ("/blog/", "/news/", "/article", "/wiki/", "/press/", "/insight", "/companies/")

# 排除标题像"定义/百科/新闻/目录"的结果
EXCLUDE_TITLE = (
    "what is",
    "what are",
    "definition",
    "meaning",
    "explained",
    "encyclopedia",
    "wiki",
    "how to",
    "guide",
    "vs.",
    " vs ",
    "in brief",
    "who is",
    "deploying",
    "opens",
    "announces",
    "announced",
    "report",
    "market size",
    "product",
    "products",
    "home",
    "about us",
    "contact us",
    "services",
    "solutions",
    "directory",
    "catalog",
    "catalogue",
    "marketplace",
    "suppliers",
)

# 排除子域名前缀（市场/商店/目录/新闻）
EXCLUDE_HOST_PREFIX = (
    "marketplace.",
    "shop.",
    "store.",
    "directory.",
    "news.",
    "blog.",
    "m.",
    "www2.",
    "catalog.",
)

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def _is_english_query(q: str) -> bool:
    return not CJK_RE.search(q or "")


class DeepSeekSearchDataSource(DataSource):
    """用 DeepSeek 官方搜索 API 发现公司（返回网页结果 → 公司线索）。"""

    def __init__(self, query: str, count: int = 10):
        self._query = query
        self._count = count

    def fetch(self) -> list[CompanyRaw]:
        try:
            r = httpx.post(
                SEARCH_URL,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": self._query,
                    "count": self._count,
                    "need_content": False,
                },
                timeout=30,
            )
            if r.status_code != 200:
                return []
            results = r.json().get("results", [])
        except Exception:  # noqa: BLE001
            return []

        companies: list[CompanyRaw] = []
        seen: set[str] = set()
        english = _is_english_query(self._query)

        for item in results:
            url = (item.get("url") or "").strip()
            low_url = url.lower()
            if not url:
                continue
            if any(d in low_url for d in EXCLUDE_DOMAINS):
                continue
            if any(p in low_url for p in EXCLUDE_PATH):
                continue

            # 主机名前缀（marketplace./shop./news. 等）
            host = low_url.replace("https://", "").replace("http://", "").split("/")[0]
            if any(host.startswith(p) for p in EXCLUDE_HOST_PREFIX):
                continue

            name = (item.get("title") or "").strip()
            # 去掉 " - xxx" / " | xxx" 后缀
            name = name.split(" - ")[0].split(" | ")[0].strip()
            if not name:
                continue

            # 英文查询出现中文标题 → 基本是无关聚合页
            if english and CJK_RE.search(name):
                continue

            # 公司名一般 2~40 字符
            if len(name) < 3 or len(name) > 40:
                continue

            # 过滤定义/百科/新闻/目录类结果
            low_name = name.lower()
            if any(x in low_name for x in EXCLUDE_TITLE):
                continue

            key = url.lower().rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            companies.append(
                CompanyRaw(
                    name=name,
                    website=url,
                    country="",
                    industry=self._query,
                    description=(item.get("summary") or "")[:1000],
                    source="deepseek",
                )
            )
        return companies
