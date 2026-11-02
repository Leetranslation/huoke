"""邮件追踪：生成 token、注入打开像素、改写点击链接。"""

import re
import secrets
from html import escape
from urllib.parse import quote

from app.core.config import settings

URL_RE = re.compile(r"(https?://[^\s<>\"']+)")

# 1x1 透明 GIF 像素
PIXEL_GIF = bytes.fromhex(
    "47494638396101000100800000ffffff000000"
    "21f90401000000002c00000000010001000002024401003b"
)


def new_token() -> str:
    """生成追踪 token（随机、不可枚举）。"""
    return secrets.token_urlsafe(24)


def build_tracked_html(body: str, token: str) -> str:
    """把正文包成 HTML：注入打开像素 + 把外链改写成点击追踪链接。"""
    base = (settings.public_base_url or "").rstrip("/")
    text = body or ""

    # 已经是 HTML 就直接用，否则按行包 <p>
    if "<" in text and ">" in text:
        html = text
    else:
        html = "".join(
            f"<p>{escape(line)}</p>" for line in text.split("\n") if line.strip()
        )

    if not base:
        return html

    # 改写外链（跳过已经是追踪链接的）
    def _wrap(m: re.Match) -> str:
        url = m.group(1)
        if f"{base}/t/c/" in url:
            return url
        return f"{base}/t/c/{token}?u={quote(url, safe='')}"

    html = URL_RE.sub(_wrap, html)
    html += (
        f'<img src="{base}/t/o/{token}.png" width="1" height="1" '
        f'style="display:none" alt="" />'
    )
    return html
