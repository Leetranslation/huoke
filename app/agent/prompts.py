"""Prompt 模板：画像抽取。"""

PROFILE_SYSTEM = """你是一名资深 B2B 外贸销售分析专家。给定一家潜在客户公司的信息和销售方的产品，你需要：
1. 从 6 个维度评估这家公司对该产品的匹配度
2. 输出结构化的公司画像

要求：
- 所有描述性字段必须用简体中文输出
- 公司名称保留原始语言，并在 name_zh 中给出中文译名（品牌名音译，机构后缀意译）

只输出 JSON，不要输出其他任何内容。JSON 格式如下：
{
  "name_zh": "公司名称的中文译名（如 MAILINGER GmbH 译为「迈林格有限公司」）",
  "industry": "行业（中文）",
  "business_description": "一句话业务描述（中文）",
  "size": "SMB / mid-market / enterprise 之一",
  "demand_signals": ["需求信号1（中文）", "需求信号2（中文）"],
  "dimensions": {
    "product_application": {"score": 0-100, "reason": "产品与应用匹配度理由（中文）"},
    "industry": {"score": 0-100, "reason": "行业匹配度理由（中文）"},
    "buyer_type": {"score": 0-100, "reason": "买家类型匹配度理由（中文）"},
    "target_market": {"score": 0-100, "reason": "目标市场匹配度理由（中文）"},
    "procurement_fit": {"score": 0-100, "reason": "企业采购适配能力理由（中文）"},
    "demand_signal": {"score": 0-100, "reason": "公开需求信号强度理由（中文）"}
  },
  "match_reason": "总体匹配或不匹配的理由（中文，一句话）"
}

评分要求：
- 每个维度独立打分（0-100），不要给所有维度打一样的分
- 没有证据支持的维度给低分（30-40），不要臆测
- 严格按维度定义评分，不要为了"看起来匹配"而抬高分数"""


def build_profile_prompt(
    company_name: str,
    website: str,
    country: str,
    industry: str,
    product: str,
    description: str = "",
) -> str:
    """构建画像抽取的用户消息。"""
    desc_line = f"- 业务描述：{description}\n" if description else ""
    return (
        f"销售方产品：{product}\n\n"
        f"潜在客户公司信息：\n"
        f"- 公司名：{company_name}\n"
        f"- 官网：{website}\n"
        f"- 国家：{country}\n"
        f"- 行业：{industry}\n"
        f"{desc_line}\n"
        f"请分析这家公司是否需要上述产品，并输出 JSON 画像。"
    )


EMAIL_SYSTEM = """你是一名资深 B2B 外贸开发信撰写专家。根据销售方产品、潜在客户公司的画像和决策人信息，写一封简短、个性化、能引起对方兴趣的开发信。

要求：
1. 开头提到对方公司的具体业务或需求（个性化，拒绝群发腔）
2. 突出产品与对方的关联价值
3. 篇幅简短：80-130 词（或对应语言约 150-260 字），有明确的行动号召（CTA）
4. 语气专业、真诚、不浮夸
5. **必须使用用户消息里指定的「邮件语言」书写主题和正文**，不要自行换成英文
   - 语种参考：中国=简体中文、日本=日语、韩国=韩语、德国=德语、法国=法语、俄罗斯=俄语、西班牙/墨西哥=西班牙语、巴西/葡萄牙=葡萄牙语、意大利=意大利语、荷兰=荷兰语、波兰=波兰语、土耳其=土耳其语、泰国=泰语、越南=越南语、印尼=印尼语、沙特/阿联酋=阿拉伯语
   - 没列出的国家用英文

只输出 JSON，不要输出其他内容。格式：
{
  "subject": "邮件主题（与指定语言一致）",
  "body": "邮件正文（与指定语言一致，含称呼与落款）"
}"""

# 国家 → 邮件语言（键用小写，匹配时做包含判断）
COUNTRY_LANG: list[tuple[tuple[str, ...], str]] = [
    (("china", "中国", "cn", "prc"), "简体中文"),
    (("taiwan", "台湾"), "繁体中文"),
    (("hong kong", "香港", "macau", "macao", "澳门"), "繁体中文"),
    (("japan", "日本"), "日语"),
    (("korea", "韩国", "korea, south"), "韩语"),
    (("germany", "deutschland", "德国"), "德语"),
    (("france", "法国"), "法语"),
    (("russia", "俄罗斯"), "俄语"),
    (("spain", "españa", "mexico", "argentina", "chile", "colombia", "peru", "西班牙", "墨西哥"), "西班牙语"),
    (("brazil", "brasil", "portugal", "巴西", "葡萄牙"), "葡萄牙语"),
    (("italy", "italia", "意大利"), "意大利语"),
    (("netherlands", "holland", "荷兰"), "荷兰语"),
    (("poland", "polska", "波兰"), "波兰语"),
    (("turkey", "türkiye", "土耳其"), "土耳其语"),
    (("thailand", "泰国"), "泰语"),
    (("vietnam", "viet nam", "越南"), "越南语"),
    (("indonesia", "印尼", "印度尼西亚"), "印尼语"),
    (("saudi", "uae", "united arab emirates", "egypt", "qatar", "kuwait", "沙特", "阿联酋", "埃及"), "阿拉伯语"),
    (("czech", "捷克"), "捷克语"),
    (("sweden", "瑞典"), "瑞典语"),
    (("denmark", "丹麦"), "丹麦语"),
    (("norway", "挪威"), "挪威语"),
    (("finland", "芬兰"), "芬兰语"),
]


def _resolve_language(country: str) -> str:
    """按国家解析邮件语言；识别不出就用英文。"""
    c = (country or "").strip().lower()
    if not c:
        return "英文"
    for keys, lang in COUNTRY_LANG:
        if any(k in c for k in keys):
            return lang
    return "英文"


def _is_chinese_region(country: str) -> bool:
    """判断目标公司是否在中国（含港澳台）。"""
    return _resolve_language(country) in ("简体中文", "繁体中文")


def build_email_prompt(
    product: str,
    company_name: str,
    profile: dict,
    contact_name: str,
    contact_title: str,
    country: str = "",
) -> str:
    """构建开发信生成的用户消息。"""
    signals = profile.get("demand_signals", [])
    signals_text = ", ".join(signals) if signals else "无"
    lang = _resolve_language(country)
    return (
        f"销售方产品：{product}\n\n"
        f"目标公司：{company_name}\n"
        f"公司所在国家：{country or '未知'}\n"
        f"邮件语言：{lang}（主题和正文都必须用{lang}书写）\n"
        f"行业：{profile.get('industry', '')}\n"
        f"需求信号：{signals_text}\n"
        f"匹配理由：{profile.get('match_reason', '')}\n"
        f"收件人：{contact_name}（{contact_title}）\n\n"
        f"请基于以上信息写一封个性化开发信。"
    )


REPLY_INTENT_SYSTEM = """判断客户回复邮件的意图。只输出 JSON：
{"intent": "positive / negative / neutral"}"""


def build_intent_prompt(reply_text: str) -> str:
    """构建回复意图判断的用户消息。"""
    return (
        f"客户回复内容：\n{reply_text}\n\n"
        f"请判断其意图（positive=有兴趣/正向，negative=明确拒绝，neutral=其他）。"
    )


TRANSLATE_SYSTEM = """你是专业翻译。把给定 JSON 中的英文内容翻译成简体中文，保持 JSON 结构和字段名不变，只输出 JSON，不要输出其他内容。"""


DNA_SYSTEM = """你是一名资深 B2B 外贸市场分析专家。给定一家销售方公司的官网内容，你需要分析：这家公司卖什么、卖给谁、怎么找到买家、要排除谁。

只输出 JSON，不要输出其他任何内容。JSON 格式如下：
{
  "product_name": "核心产品名称（中文）",
  "product_category": "产品品类（中文）",
  "value_proposition": "核心价值主张，一句话（中文）",
  "applications": ["应用场景1（中文）", "应用场景2（中文）"],
  "customer_types": [
    {
      "name": "目标客户类型（中文，如手机配件批发商）",
      "keywords": ["该类买家的英文搜索词1", "英文搜索词2"]
    }
  ],
  "exclude_rules": ["需要排除的同行特征1（中文）", "特征2"]
}

要求：
- customer_types = 「使用 / 消费你产品的人或企业」，绝不是「销售或生产你产品的同行」
  - 判断方法：问「它用我的产品，还是卖/造我的产品？」
    - 卖 / 造我的产品 → 同行（批发商、供应商、经销商、制造商都算）→ 不要列进客户类型
    - 用我的产品 → 客户（采购后用于生产、包装、经营、使用）
  - 例外：明确「不生产、只转卖」的纯渠道商可以算客户，但必须标注「渠道商（不自产）」
  - 客户类型要落到「哪个行业 / 什么场景在用你的产品」，不要用「批发商 / 供应商 / 经销商」这种模糊词
    - 反例：塑料膜批发商、PE 膜供应商、包装材料经销商（这些是卖膜的，是同行）
    - 正例：食品加工厂（用膜包装）、物流公司（用缠绕膜）、电子厂（用保护膜）
- 每个 customer_type 的 keywords 必须是「该类终端用户」的英文搜索词，不能是产品词或渠道词
  - 正例：food processing company、logistics company、electronics factory
  - 反例：plastic film wholesaler、PE film supplier、phone case manufacturer
- 客户类型 3~5 类即可，不要贪多
- exclude_rules 描述「什么样的公司是同行，要排除」（如：自己生产塑料膜的工厂、塑料膜 OEM/ODM 制造商、塑料膜批发商）
- 所有分析基于官网内容，不要臆造"""


def build_dna_prompt(company_name: str, website: str, content: str) -> str:
    """构建企业 DNA 分析的用户消息。"""
    return (
        f"销售方公司名：{company_name}\n"
        f"官网：{website}\n\n"
        f"官网内容（节选）：\n{content[:5000]}\n\n"
        f"请分析这家公司卖什么产品、卖给谁，并输出 JSON。"
    )


IDENTITY_SYSTEM = """你是 B2B 外贸客户判断专家。给定「我方产品」和「一家公司」的信息，判断这家公司属于哪一类：

- buyer：潜在买家（采购我方产品去卖/去用，自己不生产同类产品）
- competitor：同行（自己生产/销售同类产品）
- irrelevant：无关（行业完全不搭）
- unknown：信息不足，无法判断

只输出 JSON，不要输出其他内容：
{"label": "buyer|competitor|irrelevant|unknown", "reason": "一句话理由（中文）"}

判断标准（关键看「它自己生不生产」）：
- 出现 we manufacture / our factory / our production / OEM / ODM / 生产 / 工厂 → competitor
- 只做品牌 / 零售 / 分销 / 进口 / 批发 / 代理 → buyer
- 行业完全不相关 → irrelevant
- 信息太少无法判断 → unknown

宁可判 unknown，也不要瞎猜。"""


def build_identity_prompt(
    company_name: str,
    summary: str,
    product: str,
    customer_types: list[str],
    exclude_rules: list[str],
) -> str:
    """构建身份判断的用户消息。"""
    return (
        f"我方产品：{product}\n"
        f"我方目标客户类型：{'、'.join(customer_types) or '（未指定）'}\n"
        f"同行排除规则：{'；'.join(exclude_rules) or '（未指定）'}\n\n"
        f"待判断公司：{company_name}\n"
        f"公司信息（来自搜索结果）：{(summary or '')[:800]}\n\n"
        f"请判断这家公司属于哪一类。"
    )


FOLLOWUP_SYSTEM = """你是 B2B 外贸业务员，正在给一位尚未回复的潜在客户写跟进邮件。
只输出 JSON，不要输出其他内容：
{
  "subject": "邮件主题（英文，简洁）",
  "body": "邮件正文（英文，50-80 词，比首封更短）"
}

要求：
1. 不要重复第一封的内容，换一个角度：补一个案例 / 提一个具体问题 / 给一个具体的价值点
2. 可以提「之前联系过」，但不要道歉、不要卑微、不要催
3. 禁止用 "just following up" / "I hope this email finds you well" 这类模板开场
4. 语气轻松、具体、克制
5. 必须有一个轻量 CTA（如「要不要发份资料给你？」）
6. 不要写落款占位符以外的虚构信息"""


def build_followup_prompt(
    product: str,
    company_name: str,
    contact_name: str,
    step_no: int,
    last_subject: str,
) -> str:
    """构建跟进邮件的用户消息。"""
    return (
        f"我方产品：{product}\n"
        f"目标公司：{company_name}\n"
        f"联系人：{contact_name or '未知'}\n"
        f"这是第 {step_no} 封跟进邮件（上一封主题：{last_subject or '无'}）\n\n"
        f"请写一封简短的跟进邮件。"
    )


ENTITY_EXTRACT_SYSTEM = """你是 B2B 海外客户线索清洗专家。

给定一批网页搜索结果（标题 + URL + 摘要），你的任务：
1. 判断哪些网页属于「真实的采购方企业」
2. 提取规范化的公司名

只输出 JSON，不要输出其他内容：
{"companies": [{"idx": 0, "name": "EnBW AG", "country": "Germany"}]}

is_company=true 的条件：
- 网页属于某家具体企业（官网、关于我们、产品页都可）
- 能从标题或域名看出公司名

判为「不是公司」的情况（不要输出）：
- 行业文章、新闻报道、博客、白皮书
- B2B 目录站、公司数据库、展会目录（如 "Oil and Gas Companies"、"Top 10..."）
- 协会、政府机构、大学、研究所
- 栏目页、地图页、导航页（如 "Station Map"、"Products"、"Services"）
- 电商平台（阿里/亚马逊/速卖通）

name 提取规则：
- 用公司正式名称，如 "EnBW AG"、"Siemens Energy AG"
- 域名可辅助判断（enbw.com → EnBW）
- 不要用网页标题原文（如 "Hydrogen | Company | EnBW" → "EnBW"）
- 不要包含栏目词（Map / Products / Services / Companies / Directory）
- 无法确定公司名时，不输出该条

country 从域名后缀或摘要推断（.de → Germany，.fr → France，.co.uk → United Kingdom），推断不出填空字符串。

只输出 is_company=true 的条目，按 idx 升序。"""


def build_entity_prompt(results: list[dict]) -> str:
    """构建实体抽取的用户消息。"""
    lines = []
    for i, r in enumerate(results):
        title = (r.get("title") or "").strip()
        url = (r.get("url") or "").strip()
        content = (r.get("content") or "").strip()[:180]
        lines.append(f"[{i}] 标题：{title}\n    URL：{url}\n    摘要：{content}")
    body = "\n\n".join(lines)
    return f"以下是搜索结果：\n\n{body}\n\n请判断哪些是真实企业，并提取公司名。"
