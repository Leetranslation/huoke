"""邮件追踪接口：打开像素 + 点击跳转（无需登录）。"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Email, EmailEvent
from app.models.enums import EventType
from app.services.tracking_service import PIXEL_GIF

router = APIRouter(prefix="/t", tags=["tracking"])

NO_CACHE = {
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "Pragma": "no-cache",
}


def _record(db: Session, email: Email, event_type: str, meta: dict) -> None:
    db.add(EmailEvent(email_id=email.id, event_type=event_type, meta=meta))
    db.commit()


@router.get("/o/{filename}")
def track_open(filename: str, request: Request, db: Session = Depends(get_db)):
    """打开追踪：返回 1x1 透明像素，并记录 open 事件。"""
    token = filename[:-4] if filename.endswith(".png") else filename
    email = db.query(Email).filter(Email.tracking_token == token).first()
    if email is not None:
        _record(
            db,
            email,
            EventType.OPEN,
            {"ua": request.headers.get("user-agent", "")[:300]},
        )
    return Response(content=PIXEL_GIF, media_type="image/gif", headers=NO_CACHE)


@router.get("/c/{token}")
def track_click(
    token: str,
    request: Request,
    u: str = "",
    db: Session = Depends(get_db),
):
    """点击追踪：记录 click 事件后 302 跳转到原链接。"""
    email = db.query(Email).filter(Email.tracking_token == token).first()
    if email is not None and u.startswith("http"):
        _record(
            db,
            email,
            EventType.CLICK,
            {
                "url": u[:500],
                "ua": request.headers.get("user-agent", "")[:300],
            },
        )
    if u.startswith("http"):
        return RedirectResponse(url=u, status_code=302)
    return Response("ok")
