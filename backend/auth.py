import base64
import hashlib
import hmac
import time
from typing import Optional

from fastapi import Header, HTTPException, status

from .config import get_settings


def _sign(message: str) -> str:
    settings = get_settings()
    return hmac.new(
        settings.token_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_token(username: str) -> str:
    settings = get_settings()
    expires_at = int(time.time()) + settings.token_hours * 3600
    payload = f"{username}:{expires_at}"
    signature = _sign(payload)
    token_raw = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(token_raw.encode("utf-8")).decode("utf-8")


def verify_token(token: str) -> str:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        username, expires_at_raw, signature = decoded.rsplit(":", 2)
        payload = f"{username}:{expires_at_raw}"
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiges Admin-Token.",
        )

    expected = _sign(payload)
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiges Admin-Token.",
        )

    if int(expires_at_raw) < int(time.time()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin-Token ist abgelaufen.",
        )

    return username


def require_admin(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bitte als Admin einloggen.",
        )
    token = authorization.split(" ", 1)[1].strip()
    username = verify_token(token)

    settings = get_settings()
    if username != settings.admin_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin-Berechtigung fehlt.",
        )
    return username
