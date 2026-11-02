"""对比实验：画像输入信息量对匹配分的影响（A 简 vs B 丰富）。"""

import asyncio
import sys

from app.agent.llm import LLMClient
from app.agent.profiler import Profiler
from app.agent.prompts import PROFILE_SYSTEM

sys.stdout.reconfigure(encoding="utf-8")

PRODUCT_RICH = (
    "制造业 ERP 系统，覆盖生产排程、库存管理、采购管理、质量追溯、财务核算，"
    "帮助中小制造企业实现数字化管理。目标客户：50-500 人的制造企业，"
    "尤其是多品种小批量生产模式。"
)

COMPANY_RICH = """- 公司名：MAILINGER Innovative fiber solutions GmbH
- 官网：http://www.mailinger.de/
- 国家：Germany
- 行业：纤维材料制造
- 业务描述：一家德国纤维材料制造商，专注于创新纤维解决方案的研发与生产，为工业应用提供纤维复合材料和特种纤维产品。
- 规模：约 120 名员工，成立于 2007 年，年营收约 2500 万欧元
- 已发现信号：官网招聘「生产计划专员」，新闻提到「正在推进数字化工厂项目」"""

DIMS = [
    "product_application",
    "industry",
    "buyer_type",
    "target_market",
    "procurement_fit",
    "demand_signal",
]


async def main() -> None:
    llm = LLMClient()

    user_a = (
        "销售方产品：ERP system\n\n"
        "潜在客户公司信息：\n"
        "- 公司名：MAILINGER Innovative fiber solutions GmbH\n"
        "- 官网：http://www.mailinger.de/\n"
        "- 国家：Germany\n"
        "- 行业：manufacturer\n\n"
        "请分析这家公司是否需要上述产品，并输出 JSON 画像。"
    )
    a = Profiler._parse(
        await llm.chat(
            [{"role": "system", "content": PROFILE_SYSTEM}, {"role": "user", "content": user_a}]
        )
    )
    score_a = Profiler.compute_score(a.get("dimensions", {}))
    print("=== A：信息少（现状）===")
    print("分数:", score_a)
    print("理由:", a.get("match_reason"))

    user_b = (
        f"销售方产品：{PRODUCT_RICH}\n\n"
        f"潜在客户公司信息：\n{COMPANY_RICH}\n\n"
        "请分析这家公司是否需要上述产品，并输出 JSON 画像。"
    )
    b = Profiler._parse(
        await llm.chat(
            [{"role": "system", "content": PROFILE_SYSTEM}, {"role": "user", "content": user_b}]
        )
    )
    score_b = Profiler.compute_score(b.get("dimensions", {}))
    print("\n=== B：信息充足 ===")
    print("分数:", score_b)
    print("理由:", b.get("match_reason"))

    print("\n维度对比:")
    for k in DIMS:
        sa = a.get("dimensions", {}).get(k, {}).get("score")
        sb = b.get("dimensions", {}).get(k, {}).get("score")
        print(f"  {k}: A={sa} -> B={sb}")


if __name__ == "__main__":
    asyncio.run(main())
