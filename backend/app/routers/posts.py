from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func
from datetime import datetime, timezone
from ..database import get_session
from ..deps import auth_required
from ..models import Post
from ..schemas import PostCreate, PostRead, PostUpdate
from ..scheduler import schedule_post

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/", response_model=list[PostRead])
def list_posts(session: Session = Depends(get_session), user = Depends(auth_required)):
    posts = session.exec(select(Post).order_by(Post.scheduled_at.desc())).all()
    return posts

@router.post("/", response_model=PostRead)
def create_post(data: PostCreate, session: Session = Depends(get_session), user = Depends(auth_required)):
    payload = data.model_dump()
    # Normalize scheduled_at to naive UTC for consistent storage/comparison
    sa = payload.get("scheduled_at")
    if isinstance(sa, datetime) and sa.tzinfo is not None:
        payload["scheduled_at"] = sa.astimezone(timezone.utc).replace(tzinfo=None)
    post = Post(**payload, status="scheduled")
    session.add(post)
    session.commit(); session.refresh(post)
    schedule_post(session, post)
    return post

@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, session: Session = Depends(get_session), user = Depends(auth_required)):
    post = session.get(Post, post_id)
    if not post: raise HTTPException(404, "Not found")
    return post

@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, data: PostUpdate, session: Session = Depends(get_session), user = Depends(auth_required)):
    post = session.get(Post, post_id)
    if not post: raise HTTPException(404, "Not found")
    updates = data.model_dump(exclude_unset=True)
    sa = updates.get("scheduled_at")
    if isinstance(sa, datetime) and sa.tzinfo is not None:
        updates["scheduled_at"] = sa.astimezone(timezone.utc).replace(tzinfo=None)
    for k, v in updates.items():
        setattr(post, k, v)
    post.updated_at = datetime.utcnow()
    session.add(post); session.commit(); session.refresh(post)
    schedule_post(session, post)
    return post

@router.delete("/{post_id}")
def delete_post(post_id: int, session: Session = Depends(get_session), user = Depends(auth_required)):
    post = session.get(Post, post_id)
    if not post: raise HTTPException(404, "Not found")
    post.status = "canceled"
    session.add(post); session.commit()
    return {"ok": True}

@router.post("/{post_id}/publish-now")
def publish_now(post_id: int, session: Session = Depends(get_session), user = Depends(auth_required)):
    post = session.get(Post, post_id)
    if not post: raise HTTPException(404, "Not found")
    from ..services.posting import publish_post
    import asyncio
    asyncio.run(publish_post(session, post_id))
    return {"status": "triggered"}

@router.get("/stats")
def posts_stats(session: Session = Depends(get_session), user = Depends(auth_required)):
    now = datetime.utcnow()
    # Use SQL COUNT for efficiency
    stmt = select(func.count()).select_from(Post).where(Post.status == "scheduled", Post.scheduled_at > now)
    pending = session.exec(stmt).one()
    # Normalize response
    return {"pending": int(pending or 0), "now": now.isoformat() + "Z"}
