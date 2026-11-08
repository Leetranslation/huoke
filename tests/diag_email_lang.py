"""验证：多语言开发信（日本→日语、俄罗斯→俄语…）。"""

import asyncio
import sys

from app.agent.email_writer import EmailWriter
from app.agent.llm import LLMClient
from app.agent.prompts import _resolve_language

sys.stdout.reconfigure(encoding="utf-8")

CASES = [
    ("Yamazaki Hydraulics", "Japan"),
    ("Гидравлика Сибирь", "Russia"),
    ("Bosch Rexroth GmbH", "Germany"),
    ("Hydrotech France", "France"),
    ("Hidráulica Ibérica", "Spain"),
    ("Hidráulica Brasil", "Brazil"),
    ("مجموعة الطاقة", "Saudi Arabia"),
    ("Hyundai Precision", "Korea"),
]


def detect(text: str) -> str:
    if any("\u3040" <= ch <= "\u30ff" for ch in text):
        return "日语"
    if any("\u0400" <= ch <= "\u04ff" for ch in text):
        return "俄语"
    if any("\u0600" <= ch <= "\u06ff" for ch in text):
        return "阿拉伯语"
    if any("\uac00" <= ch <= "\ud7af" for ch in text):
        return "韩语"
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        return "中文"
    return "拉丁字母"


async def main() -> None:
    print("=== 语言映射 ===")
    for _, country in CASES:
        print(f"  {country:16} → {_resolve_language(country)}")

    print("\n=== 实际生成 ===")
    writer = EmailWriter(LLMClient())
    profile = {"industry": "工业设备", "match_reason": "需要高压液压元件"}

    for name, country in CASES:
        lang = _resolve_language(country)
        draft = await writer.write(
            "高压液压与气动元件", name, profile,
            contact_name="Procurement", contact_title="Purchasing Manager", country=country,
        )
        got = detect(draft.subject + draft.body)
        print(f"\n{name} ({country}) 期望={lang} 实际={got}")
        print(f"  主题：{draft.subject[:60]}")
        print(f"  正文：{draft.body[:90].replace(chr(10), ' ')}...")


if __name__ == "__main__":
    asyncio.run(main())
