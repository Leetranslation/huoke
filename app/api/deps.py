"""FastAPI 依赖注入。"""

from app.agent.email_writer import EmailWriter
from app.agent.llm import LLMClient
from app.agent.profiler import Profiler
from app.core.config import settings
from app.senders.base import EmailSender
from app.senders.mock_sender import MockEmailSender
from app.senders.smtp_sender import SMTPSender


def get_llm() -> LLMClient:
    return LLMClient()


def get_profiler() -> Profiler:
    return Profiler(get_llm())


def get_email_writer() -> EmailWriter:
    return EmailWriter(get_llm())


def get_email_sender() -> EmailSender:
    """有 SMTP 配置就用真实发信，否则用 Mock（不影响开发/演示）。"""
    if settings.smtp_host and settings.smtp_user and settings.smtp_password:
        return SMTPSender()
    return MockEmailSender()
