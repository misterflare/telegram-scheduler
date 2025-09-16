import asyncio
from sqlmodel import Session, select
from datetime import datetime
from ..models import Post, AppSettings
from ..telegram_client import send_post

async def publish_post(session: Session, post_id: int):
    post = session.get(Post, post_id)
    if not post or post.status in ("posted", "canceled"):
        return
    settings = session.exec(select(AppSettings)).first()
    if not settings or not settings.bot_token or not settings.channel_id:
        post.status = "failed"
        post.error = "Bot token/channel not set"
        session.add(post); session.commit()
        return
    try:
        await send_post(post.text, post.buttons, post.media, settings.channel_id, token=settings.bot_token)
        post.status = "posted"
        post.error = None
    except Exception as e:
        post.status = "failed"
        post.error = str(e)[0:500]
    finally:
        post.updated_at = datetime.utcnow()
        session.add(post)
        session.commit()
