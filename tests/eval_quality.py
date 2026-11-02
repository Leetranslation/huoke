"""LLM 判断质量评测：回复意图识别 + 买家身份判定。

只调 LLM，不写数据库、不发邮件。
用法：
    python -m tests.eval_quality            # 全量（40 条，约 0.05 元）
    python -m tests.eval_quality --limit 10 # 只跑前 10 条（约 0.01 元）
"""

import json
import sys

import httpx

from app.agent.prompts import IDENTITY_SYSTEM, build_identity_prompt
from app.core.config import settings
from app.models.enums import ContactStatus  # noqa: F401  (确保枚举可用)
from app.tasks.followup import _classify_intent

sys.stdout.reconfigure(encoding="utf-8")

# ---------- 意图样本（人工标注）----------
INTENT_CASES: list[tuple[str, str]] = [
    # positive
    ("好的，我们很有兴趣，方便发一下详细资料吗？", "positive"),
    ("能报个 FOB 价格吗？我们需要 500 套", "positive"),
    ("可以聊聊，下周约个视频会议", "positive"),
    ("Thanks, please send me the catalog and price list.", "positive"),
    ("我们有采购计划，加个微信详聊", "positive"),
    ("样品能寄过来看看吗", "positive"),
    ("Sounds interesting, who should I talk to?", "positive"),
    ("请把技术规格书发给我", "positive"),
    # negative
    ("不要再向我发了", "negative"),
    ("不好意思，不需要", "negative"),
    ("请把我从你们的邮件列表移除", "negative"),
    ("Not interested, please stop emailing me.", "negative"),
    ("我们已经有稳定供应商了，谢谢", "negative"),
    ("Unsubscribe", "negative"),
    ("别发了，烦不烦", "negative"),
    ("不需要，我们不做这块", "negative"),
    # neutral
    ("收到", "neutral"),
    ("你是谁？", "neutral"),
    ("What is this about?", "neutral"),
    ("How did you get my email?", "neutral"),
]

# ---------- 身份样本（人工标注）----------
PRODUCT = "高压液压与气动元件"
CUSTOMER_TYPES = ["液压设备制造商", "工程机械厂商", "工业自动化集成商"]
EXCLUDE_RULES = ["液压元件经销商", "同类液压元件生产商"]

IDENTITY_CASES: list[tuple[str, str, str]] = [
    # ---- buyer：用液压元件的整机厂 / 工程商 ----
    ("Liebherr Hydraulikbagger GmbH", "Manufacturer of hydraulic excavators and construction machinery.", "buyer"),
    ("Caterpillar Inc", "World leading manufacturer of construction and mining equipment.", "buyer"),
    ("Bosch Rexroth Assembly Plant", "Produces hydraulic power units and assembles industrial machinery.", "buyer"),
    ("Konecranes Oyj", "Lifting equipment manufacturer, uses hydraulic systems in port cranes.", "buyer"),
    ("Manitou Group", "Material handling and aerial work platform manufacturer.", "buyer"),
    ("Schaeffler Hydraulics Division", "Produces linear motion and hydraulic actuation components for machinery OEMs.", "buyer"),
    ("Nordic Wind Service AS", "Wind turbine maintenance company, uses hydraulic tools for blade repair.", "buyer"),
    ("Steel Dynamics Inc", "Steel mill operator, heavy reliance on hydraulic presses.", "buyer"),
    # ---- competitor：同类元件生产商 ----
    ("Bosch Rexroth AG", "Global manufacturer of hydraulic pumps, valves and cylinders.", "competitor"),
    ("Parker Hannifin Corporation", "Manufactures hydraulic and pneumatic motion control components.", "competitor"),
    ("SMC Corporation", "Leading producer of pneumatic automation components.", "competitor"),
    ("Hydro-Funk GmbH", "German manufacturer of hydraulic components and systems.", "competitor"),
    ("HAWE Hydraulik SE", "Develops and produces hydraulic pumps, valves, and power packs.", "competitor"),
    ("Stauff GmbH", "Manufactures hydraulic fittings, clamps and fluid technology components.", "competitor"),
    # ---- irrelevant：与液压采购无关 ----
    ("University of Dayton Research Institute", "Academic research organization focused on aerospace materials.", "irrelevant"),
    ("Red Cross Society", "Humanitarian aid organization.", "irrelevant"),
    ("Starbucks Coffee Company", "Global coffeehouse chain.", "irrelevant"),
    ("Munich Re Insurance", "Reinsurance company providing risk transfer services.", "irrelevant"),
    ("Deutsche Bank AG", "Global investment and retail bank.", "irrelevant"),
    ("FC Bayern München", "Professional football club.", "irrelevant"),
]


def _chat_sync(messages: list[dict]) -> str:
    """同步调 LLM（评测用，避免 event loop 问题）。"""
    r = httpx.post(
        f"{settings.llm_base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        json={"model": settings.llm_model, "messages": messages, "temperature": 0.1},
        timeout=60,
    )
    if r.status_code != 200:
        return ""
    return r.json()["choices"][0]["message"]["content"] or ""


def _parse_json(text: str) -> dict:
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.startswith("json"):
            t = t[4:]
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        s, e = t.find("{"), t.rfind("}")
        if s != -1 and e != -1:
            try:
                return json.loads(t[s : e + 1])
            except json.JSONDecodeError:
                pass
    return {}


def eval_intent(limit: int | None) -> tuple[int, int, list]:
    cases = INTENT_CASES[:limit] if limit else INTENT_CASES
    print(f"\n{'='*60}\n回复意图识别 · {len(cases)} 条\n{'='*60}")
    ok = 0
    fails = []
    for i, (body, truth) in enumerate(cases, 1):
        pred = _classify_intent(body)
        hit = pred == truth
        ok += hit
        mark = "✓" if hit else "✗"
        print(f"{mark} [{i:2}] 标注={truth:9} 预测={pred:9} | {body[:30]}")
        if not hit:
            fails.append((body, truth, pred))
    print(f"\n准确率：{ok}/{len(cases)} = {ok/len(cases)*100:.1f}%")
    return ok, len(cases), fails


def eval_identity(limit: int | None) -> tuple[int, int, list]:
    cases = IDENTITY_CASES[:limit] if limit else IDENTITY_CASES
    print(f"\n{'='*60}\n买家身份判定 · {len(cases)} 家\n{'='*60}")
    ok = 0
    fails = []
    for i, (name, desc, truth) in enumerate(cases, 1):
        text = _chat_sync(
            [
                {"role": "system", "content": IDENTITY_SYSTEM},
                {
                    "role": "user",
                    "content": build_identity_prompt(
                        name, desc, PRODUCT, CUSTOMER_TYPES, EXCLUDE_RULES
                    ),
                },
            ]
        )
        pred = (_parse_json(text).get("label") or "unknown").lower()
        hit = pred == truth
        ok += hit
        mark = "✓" if hit else "✗"
        print(f"{mark} [{i:2}] 标注={truth:10} 预测={pred:10} | {name[:34]}")
        if not hit:
            fails.append((name, truth, pred))
    print(f"\n准确率：{ok}/{len(cases)} = {ok/len(cases)*100:.1f}%")
    return ok, len(cases), fails


def main() -> None:
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    n = (limit or 20) * 2
    print(f"预计调用 {n} 次 LLM ≈ ¥{n * 0.0015:.3f}")

    i_ok, i_total, i_fails = eval_intent(limit)
    d_ok, d_total, d_fails = eval_identity(limit)

    print(f"\n{'='*60}\n汇总\n{'='*60}")
    print(f"意图识别：{i_ok}/{i_total} = {i_ok/i_total*100:.1f}%")
    print(f"身份判定：{d_ok}/{d_total} = {d_ok/d_total*100:.1f}%")

    if i_fails:
        print("\n意图误判：")
        for body, truth, pred in i_fails:
            print(f"  「{body[:30]}」 标注={truth} 预测={pred}")
    if d_fails:
        print("\n身份误判：")
        for name, truth, pred in d_fails:
            print(f"  {name} 标注={truth} 预测={pred}")


if __name__ == "__main__":
    main()
