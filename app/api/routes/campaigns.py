"""获客任务相关路由。"""

import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent.identity import IdentityClassifier
from app.agent.profiler import Profiler
from app.api.deps import get_llm, get_profiler
from app.core.database import get_db
from app.datasources.base import CompanyRaw
from app.datasources.contact_extractor import ContactExtractor
from app.datasources.csv_source import CsvDataSource
from app.agent.entity_extractor import EntityExtractor
from app.datasources.deepseek_search_source import DeepSeekSearchDataSource
from app.datasources.tavily_source import TavilyDataSource
from app.datasources.email_searcher import EmailSearcher
from app.datasources.europages_source import EuropagesDataSource
from app.models import Campaign, Company, Contact, User
from app.schemas import CampaignCreate, CampaignOut, CompanyOut
from app.services.dna_service import DnaService
from app.services.lead_service import LeadService
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def _ensure_user(db: Session) -> User:
    user = db.query(User).first()
    if user is None:
        user = User(email="demo@example.com", password_hash="x")
        db.add(user)
        db.flush()
    return user


@router.post("", response_model=CampaignOut)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    user = _ensure_user(db)
    campaign = Campaign(
        user_id=user.id,
        name=payload.name,
        product_name=payload.product_name,
        website=payload.website,
        target_market=payload.target_market,
        keywords=payload.keywords,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).order_by(Campaign.id.desc()).all()


@router.post("/{campaign_id}/import", response_model=list[CompanyOut])
def import_leads(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    source = CsvDataSource(Path("data/sample_companies.csv"))
    return LeadService(db).import_from(campaign, source)


@router.post("/{campaign_id}/profile", response_model=list[CompanyOut])
async def profile_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    profiler: Profiler = Depends(get_profiler),
):
    campaign = db.get(Campaign, campaign_id)
    return await ProfileService(db, profiler).profile_campaign(campaign)


@router.get("/{campaign_id}/companies", response_model=list[CompanyOut])
def list_companies(campaign_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Company)
        .filter(Company.campaign_id == campaign_id)
        .order_by(Company.match_score.desc())
        .all()
    )


ARTICLE_PATTERNS = (
    "how to",
    "how can",
    "how do",
    "what is",
    "what are",
    "archives",
    "guide",
    " vs ",
    "definition",
    "meaning",
    "explained",
    "wiki",
    "top 10",
    "best ",
    "announces",
    "announced",
    "launches",
    "unveils",
    "acquires",
    "appoints",
    "partners with",
    "report",
    "market size",
    "press release",
    "news",
)

# 机构类不是采购商（提前过滤，省画像成本）
INSTITUTION_KEYWORDS = (
    "university",
    "institute",
    "college",
    "school",
    "academy",
    "government",
    "ministry",
    "municipal",
    "department of",
    "test wing",
    "military",
    "air force",
    "navy",
    "foundation",
    "association",
    "chamber of commerce",
)


def _looks_like_article(name: str) -> bool:
    """标题像文章 / 机构 / 泛称 → 不是公司名。"""
    raw = (name or "").strip()
    low = raw.lower()
    # 公司名极少超过 60 字符
    if len(raw) > 60:
        return True
    if any(p in low for p in ARTICLE_PATTERNS):
        return True
    if any(p in low for p in INSTITUTION_KEYWORDS):
        return True
    return False


# ------ 邮箱质量分级 ------
# 明显没用的邮箱前缀（HR/招聘/系统通知/法务）
USELESS_EMAIL_PREFIX = (
    "hr@",
    "jobs@",
    "job@",
    "career",
    "recruit",
    "notify@",
    "notification",
    "noreply@",
    "no-reply@",
    "donotreply",
    "support@",
    "billing@",
    "privacy@",
    "legal@",
    "press@",
    "media@",
    "webmaster@",
    "abuse@",
    "postmaster@",
    "admin@",
    "it@",
)

# 采购/商务相关（优先触达）
PRIORITY_EMAIL_PREFIX = (
    "purchas",
    "procure",
    "sourcing",
    "buyer",
    "export@",
    "import@",
    "sales@",
    "info@",
    "contact@",
    "enquir",
    "inquir",
)


def _rank_emails(emails: list[str]) -> list[str]:
    """按触达价值排序，并剔除明显无用的邮箱。"""

    def score(e: str) -> int:
        low = (e or "").lower()
        # 学校 / 政府域名不是采购决策人
        if low.endswith(".edu") or ".edu." in low or low.endswith(".gov") or ".gov." in low:
            return -1
        if any(low.startswith(p) for p in USELESS_EMAIL_PREFIX):
            return -1
        if any(low.startswith(p) for p in PRIORITY_EMAIL_PREFIX):
            return 2
        return 1

    scored = [(score(e), i, e) for i, e in enumerate(emails)]
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [e for s, _, e in scored if s >= 0]


def _ensure_test_contact(db: Session, campaign_id: int) -> None:
    """确保任务里有一个测试客户（用于验证邮件追踪，只加一次）。"""
    from app.core.config import settings

    email = (settings.test_contact_email or "").strip()
    if not email:
        return
    exists = (
        db.query(Company)
        .filter(Company.campaign_id == campaign_id, Company.source == "test")
        .first()
    )
    if exists is not None:
        return
    company = Company(
        campaign_id=campaign_id,
        name="测试客户（追踪验证）",
        website="",
        country="TEST",  # 不写 China，避免在客户池里被误认为中国买家
        industry="测试",
        description="用于验证邮件打开/点击追踪的固定测试客户",
        identity="buyer",
        identity_reason="固定测试客户，不进入真实跟进",
        source="test",
    )
    db.add(company)
    db.flush()
    db.add(
        Contact(
            company_id=company.id,
            name="Test Recipient",
            title="",
            email=email,
        )
    )


@router.post("/{campaign_id}/crawl", response_model=list[CompanyOut])
async def crawl_leads(
    campaign_id: int,
    customer_types: str = "",
    max_companies: int = 5,
    data_source: str = "tavily",
    db: Session = Depends(get_db),
    llm=Depends(get_llm),
):
    """按企业 DNA 的目标客户类型分类型搜索，并做身份分类（买家/同行/无关/不明）。"""
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(404, "campaign not found")

    dna = campaign.dna or {}
    country = (campaign.target_market or [""])[0]

    # 优先用 DNA 的分类型客户；否则用前端传入的
    specs: list[dict] = []
    for t in dna.get("customer_types") or []:
        if isinstance(t, dict) and t.get("keywords"):
            specs.append({"name": t.get("name", ""), "keywords": list(t["keywords"])})
        elif isinstance(t, str):
            specs.append({"name": t, "keywords": [t]})
    if not specs:
        fallback = [x.strip() for x in customer_types.split(",") if x.strip()]
        specs = [{"name": x, "keywords": [x]} for x in (fallback or ["manufacturer"])]

    product = dna.get("product_name") or campaign.product_name or campaign.name
    type_names = [s["name"] for s in specs]
    exclude_rules = dna.get("exclude_rules") or []

    per_type = max(1, max_companies // len(specs))
    classifier = IdentityClassifier(llm)

    # 1. 分类型搜索 —— 并发执行（原来是串行，10 次搜索 + 10 次抽取要 37 秒）
    extractor = EntityExtractor(llm)
    tasks: list[tuple[str, str]] = [
        (spec["name"], kw) for spec in specs for kw in spec["keywords"][:2]
    ]
    sem_search = asyncio.Semaphore(5)

    async def search_one(industry: str, kw: str) -> list[CompanyRaw]:
        """单个关键词：搜索 + LLM 实体抽取，返回该关键词下的公司。"""
        query = f"{kw} {country}".strip()
        async with sem_search:
            try:
                if data_source == "tavily":
                    source = TavilyDataSource(query, count=per_type)
                    # 同步 httpx 放线程池，避免阻塞事件循环
                    await asyncio.to_thread(source.fetch)
                    items = await extractor.extract(source.raw_results)
                    out = []
                    for item in items:
                        out.append(
                            CompanyRaw(
                                name=item["name"],
                                website=item["website"],
                                country=item["country"],
                                industry=industry,
                                description=item["description"],
                                source="tavily",
                            )
                        )
                    return out
                if data_source == "europages":
                    source = EuropagesDataSource(query, max_companies=per_type)
                    raws = await asyncio.to_thread(source.fetch)
                else:
                    source = DeepSeekSearchDataSource(query, count=per_type)
                    raws = await asyncio.to_thread(source.fetch)
                for raw in raws:
                    raw.industry = industry
                return raws
            except Exception:  # noqa: BLE001
                return []

    batches = await asyncio.gather(
        *[search_one(industry, kw) for industry, kw in tasks]
    )
    raws = []
    seen: set[str] = set()
    for batch in batches:
        for raw in batch:
            key = (raw.website or raw.name).lower().rstrip("/")
            if key and key not in seen:
                seen.add(key)
                raws.append(raw)

    # 2. 规则过滤（文章页）+ 3. 身份分类
    created: list[Company] = []
    existing_names = {
        (n or "").lower().strip()
        for (n,) in db.query(Company.name)
        .filter(Company.campaign_id == campaign_id)
        .all()
    }
    for raw in raws[: max_companies * 3]:
        if len(created) >= max_companies:
            break
        if _looks_like_article(raw.name):
            continue
        name_key = (raw.name or "").lower().strip()
        if name_key in existing_names:
            continue  # 已存在（跨次爬取去重）
        try:
            identity = await classifier.classify(
                raw.name, raw.description, product, type_names, exclude_rules
            )
        except Exception:  # noqa: BLE001
            identity = None
        if identity is not None and identity.label == "irrelevant":
            continue
        company = Company(
            campaign_id=campaign.id,
            name=raw.name,
            website=raw.website,
            country=raw.country,
            industry=raw.industry,
            description=raw.description,
            identity=identity.label if identity else "unknown",
            identity_reason=identity.reason if identity else "",
            source=raw.source,
        )
        db.add(company)
        created.append(company)
        existing_names.add(name_key)

    _ensure_test_contact(db, campaign_id)
    db.commit()
    for c in created:
        db.refresh(c)
    return created


@router.post("/{campaign_id}/extract-contacts")
async def extract_contacts(
    campaign_id: int,
    use_search: bool = True,
    db: Session = Depends(get_db),
):
    """提取联系人（并发）：先爬官网，拿不到再用 DeepSeek Search 搜（约 0.005 元/家）。"""
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(404, "campaign not found")

    companies = db.query(Company).filter(Company.campaign_id == campaign_id).all()
    # 预查已有联系人的公司，避免在并发块里做同步 DB 查询（会阻塞事件循环）
    company_ids = [c.id for c in companies]
    existing_ids: set[int] = set()
    if company_ids:
        existing_ids = {
            cid
            for (cid,) in db.query(Contact.company_id)
            .filter(Contact.company_id.in_(company_ids))
            .distinct()
        }

    extractor = ContactExtractor()
    searcher = EmailSearcher() if use_search else None
    sem = asyncio.Semaphore(10)  # 原来是 5，12 家公司要跑 3 批

    async def one(company: Company) -> int:
        if company.id in existing_ids:
            return 0
        async with sem:
            try:
                emails: list[str] = []
                # 有官网才爬，没官网直接走搜索
                if company.website:
                    emails = [
                        c.email
                        for c in await extractor.extract(company.website, max_emails=2)
                    ]
                if not emails and searcher:
                    emails = await searcher.search(company.name, company.website)
                emails = _rank_emails(emails)  # 剔除 HR/系统邮箱，采购类排前面
            except Exception:  # noqa: BLE001
                return 0
            for email in emails[:2]:
                db.add(
                    Contact(
                        company_id=company.id,
                        name="Contact",
                        title="",
                        email=email,
                    )
                )
            return len(emails[:2])

    counts = await asyncio.gather(*[one(c) for c in companies])
    db.commit()
    extractor.close()
    return {"created": sum(counts), "companies": len(companies)}


@router.post("/{campaign_id}/analyze-dna")
async def analyze_dna(
    campaign_id: int,
    db: Session = Depends(get_db),
    llm=Depends(get_llm),
):
    """分析销售方官网，生成企业 DNA（产品 + 目标客户 + 搜索关键词，约 1 分钱）。"""
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(404, "campaign not found")
    try:
        dna = await DnaService(llm).analyze(campaign)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    campaign.dna = dna
    # 同步搜索关键词，供爬取使用
    if dna.get("search_keywords"):
        campaign.keywords = dna["search_keywords"]
    db.commit()
    return dna
