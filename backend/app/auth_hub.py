from __future__ import annotations
from fastapi import Cookie, Header, HTTPException, Request, Response

from app.config import Settings

HUB_COOKIE = "ff_hub_auth"


def password_ok(settings: Settings, provided: str | None) -> bool:
    if not settings.hub_password:
        return True
    return bool(provided) and provided == settings.hub_password


def require_hub(
    request: Request,
    settings: Settings,
    x_hub_password: str | None = Header(default=None, alias="X-Hub-Password"),
    ff_hub_auth: str | None = Cookie(default=None, alias=HUB_COOKIE),
) -> None:
    if request.url.path in ("/api/health", "/api/auth/login", "/api/auth/logout"):
        return
    if request.url.path.startswith("/assets") or request.url.path in ("/", "/index.html"):
        return
    if not request.url.path.startswith("/api"):
        return
    if password_ok(settings, x_hub_password) or password_ok(settings, ff_hub_auth):
        return
    raise HTTPException(status_code=401, detail="Hub password required")


def set_auth_cookie(response: Response, password: str) -> None:
    response.set_cookie(HUB_COOKIE, password, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 30)
