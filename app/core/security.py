"""安全：JWT 令牌 + 密码哈希。"""

from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"

# bcrypt 5.x 对超过 72 字节的密码直接抛 ValueError（而不是截断），
# 这里统一按字节长度校验，把 500 变成可预期的 400/422。
MAX_PASSWORD_BYTES = 72


class PasswordTooLongError(ValueError):
    """密码超过 bcrypt 能处理的 72 字节上限。"""


class InvalidTokenError(ValueError):
    """JWT 过期、签名不匹配或格式非法。"""


def _encode_password(password: str) -> bytes:
    raw = password.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        raise PasswordTooLongError(
            f"密码不能超过 {MAX_PASSWORD_BYTES} 字节（当前 {len(raw)} 字节）"
        )
    return raw


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_encode_password(password), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_encode_password(plain), hashed.encode())
    except (PasswordTooLongError, ValueError):
        # 长度超限或哈希格式非法，一律视为校验失败，不向上抛 500。
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """解码并校验 JWT；任何失败都转成 InvalidTokenError，由 API 层映射为 401。"""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

