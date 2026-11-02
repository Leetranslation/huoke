"""邮件发送接口：可插拔。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SendResult:
    ok: bool
    message: str = ""


class EmailSender(ABC):
    """邮件发送抽象接口。新增发送方式只需实现 send，不改业务代码。"""

    @abstractmethod
    def send(self, to: str, subject: str, body: str, html: str = "") -> SendResult:
        """发送一封邮件。html 非空时优先使用（用于追踪像素/富文本）。"""
        raise NotImplementedError
