from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func
from datetime import datetime, timezone

from ..database import get_session
from ..deps import auth_required
from ..models import Post
from ..schemas import PostCreate, PostRead, PostUpdate
from ..scheduler import schedule_post
from ..telegram_client import normalize_button_url
from ..utils.timezone import resolve_timezone

def _sanitize_buttons(buttons: list[dict] | None) -> list[dict] | None:
    if not buttons:
        return None
    sanitized: list[dict] = []
    for btn in buttons:
        title = (btn.get('title') or '').strip()
        url = normalize_button_url(btn.get('url'))
        if title and url:
            sanitized.append({'title': title, 'url': url})
    return sanitized or None


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostRead])
def list_posts(session: Session = Depends(get_session), user=Depends(auth_required)):
    posts = session.exec(select(Post).order_by(Post.scheduled_at.desc())).all()
    return posts


@router.post("/", response_model=PostRead)
def create_post(data: PostCreate, session: Session = Depends(get_session), user=Depends(auth_required)):
    payload = data.model_dump()
    payload["buttons"] = _sanitize_buttons(payload.get("buttons"))
    sa = payload.get("scheduled_at")
    if isinstance(sa, datetime) and sa.tzinfo is not None:
        sa = sa.astimezone(timezone.utc).replace(tzinfo=None)
        payload["scheduled_at"] = sa
    if not isinstance(sa, datetime):
        raise HTTPException(400, "scheduled_at is required")
    if sa <= datetime.utcnow():
        raise HTTPException(400, "Publish time must be in the future")
    post = Post(**payload, status="scheduled")
    session.add(post)
    session.commit()
    session.refresh(post)
    schedule_post(session, post)
    return post


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, session: Session = Depends(get_session), user=Depends(auth_required)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Not found")
    return post


@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, data: PostUpdate, session: Session = Depends(get_session), user=Depends(auth_required)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Not found")
    updates = data.model_dump(exclude_unset=True)
    if "buttons" in updates:
        updates["buttons"] = _sanitize_buttons(updates.get("buttons"))
    original_scheduled = post.scheduled_at
    scheduled_changed = False
    if "scheduled_at" in updates:
        sa = updates.get("scheduled_at")
        if isinstance(sa, datetime) and sa.tzinfo is not None:
            sa = sa.astimezone(timezone.utc).replace(tzinfo=None)
            updates["scheduled_at"] = sa
        if not isinstance(sa, datetime):
            raise HTTPException(400, "scheduled_at is required")
        if sa <= datetime.utcnow():
            raise HTTPException(400, "Publish time must be in the future")
        scheduled_changed = (sa != original_scheduled)
    for k, v in updates.items():
        setattr(post, k, v)
    if scheduled_changed and post.status != "scheduled":
        post.status = "scheduled"
        post.error = None
    post.updated_at = datetime.utcnow()
    session.add(post)
    session.commit()
    session.refresh(post)
    schedule_post(session, post)
    return post


@router.delete("/{post_id}")
def delete_post(post_id: int, session: Session = Depends(get_session), user=Depends(auth_required)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Not found")
    post.status = "canceled"
    session.add(post)
    session.commit()
    return {"ok": True}


@router.post("/{post_id}/publish-now")
def publish_now(post_id: int, session: Session = Depends(get_session), user=Depends(auth_required)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Not found")
    from ..services.posting import publish_post
    import asyncio

    asyncio.run(publish_post(session, post_id))
    return {"status": "triggered"}


@router.get("/stats")
def posts_stats(session: Session = Depends(get_session), user=Depends(auth_required)):
    now_utc = datetime.utcnow()
    stmt = select(func.count()).select_from(Post).where(Post.status == "scheduled", Post.scheduled_at > now_utc)
    pending = session.exec(stmt).one()
    tz = resolve_timezone(session)
    aware_now = now_utc.replace(tzinfo=timezone.utc).astimezone(tz)
    tz_name = getattr(tz, "key", str(tz))
    return {"pending": int(pending or 0), "now": aware_now.isoformat(), "timezone": tz_name}
