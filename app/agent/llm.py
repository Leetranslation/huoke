"""LLM 统一封装：接任意 OpenAI 兼容模型，内置重试 + token 统计（异步）。"""

import logging

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI 兼容的异步 LLM 客户端封装。换模型只改配置，不改代码。"""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self._client = AsyncOpenAI(
            api_key=api_key or settings.llm_api_key,
            base_url=base_url or settings.llm_base_url,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_retries: int = 3,
    ) -> str:
        """发一次对话请求（异步），返回助手文本。内置重试与 token 用量日志。"""
        model = model or settings.llm_model
        last_err: Exception | None = None
        for attempt in range(max_retries):
            try:
                resp = await self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                usage = resp.usage
                if usage:
                    logger.info(
                        "llm ok | model=%s | prompt=%s completion=%s",
                        model,
                        usage.prompt_tokens,
                        usage.completion_tokens,
                    )
                return resp.choices[0].message.content or ""
            except Exception as e:  # noqa: BLE001
                last_err = e
                logger.warning(
                    "llm fail (attempt %s/%s): %s", attempt + 1, max_retries, e
                )
        raise RuntimeError(f"LLM 调用失败（重试 {max_retries} 次）: {last_err}")
