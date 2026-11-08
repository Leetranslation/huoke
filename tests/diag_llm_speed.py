"""诊断：LLM 单次/并发耗时，判断「生成开发信慢」卡在哪一层。"""

import asyncio
import sys
import time

from openai import AsyncOpenAI

from app.core.config import settings

sys.stdout.reconfigure(encoding="utf-8")

MESSAGES = [
    {"role": "system", "content": "You are a B2B sales copywriter. Output JSON: {\"subject\": \"...\", \"body\": \"...\"}"},
    {"role": "user", "content": "Write a short cold email to Mercedes-Benz USA about hydraulic components."},
]


async def one_call(idx: int, client: AsyncOpenAI) -> None:
    t = time.time()
    try:
        r = await client.chat.completions.create(
            model=settings.llm_model, messages=MESSAGES, temperature=0.3
        )
        cost = time.time() - t
        usage = r.usage
        print(f"[{idx}] 成功 {cost:.1f}s | prompt={usage.prompt_tokens} completion={usage.completion_tokens}")
    except Exception as e:  # noqa: BLE001
        print(f"[{idx}] 失败 {time.time()-t:.1f}s | {type(e).__name__}: {str(e)[:150]}")


async def main() -> None:
    # 模拟后端行为：每次请求新建 client（和 get_llm() 一致）
    print("=== 1. 单次调用（新建 client）===")
    await one_call(1, AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url))

    print("\n=== 2. 单次调用（复用 client）===")
    shared = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    await one_call(2, shared)

    print("\n=== 3. 两个并发（各自新建 client）===")
    t = time.time()
    await asyncio.gather(
        one_call(3, AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)),
        one_call(4, AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)),
    )
    print(f"总耗时 {time.time()-t:.1f}s")

    print("\n=== 4. 两个并发（复用同一 client）===")
    t = time.time()
    await asyncio.gather(one_call(5, shared), one_call(6, shared))
    print(f"总耗时 {time.time()-t:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
