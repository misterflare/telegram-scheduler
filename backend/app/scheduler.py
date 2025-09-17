from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timezone as dt_timezone
from sqlmodel import Session, select
import asyncio

from .database import engine
from .models import Post
from .services.posting import publish_post
from .utils.timezone import resolve_timezone

scheduler: BackgroundScheduler | None = None


def start_scheduler():
    global scheduler
    if scheduler:
        return scheduler
    scheduler = BackgroundScheduler(jobstores={"default": SQLAlchemyJobStore(engine=engine)})
    scheduler.start()
    return scheduler


def run_publish_job(post_id: int):
    with Session(engine) as session:
        asyncio.run(publish_post(session, post_id))


def _prepare_run_date(session: Session, post: Post) -> datetime:
    tz = resolve_timezone(session)
    scheduled_utc = post.scheduled_at.replace(tzinfo=dt_timezone.utc)
    return scheduled_utc.astimezone(tz)


def schedule_post(session: Session, post: Post):
    sched = start_scheduler()
    job_id = f"post_{post.id}"
    try:
        sched.remove_job(job_id)
    except Exception:
        pass

    scheduled_utc = post.scheduled_at.replace(tzinfo=dt_timezone.utc)
    if post.status == "scheduled" and scheduled_utc > datetime.now(dt_timezone.utc):
        run_date = _prepare_run_date(session, post)
        sched.add_job(
            run_publish_job,
            args=[post.id],
            trigger="date",
            run_date=run_date,
            id=job_id,
            replace_existing=True,
        )


def bootstrap_pending(session: Session):
    for post in session.exec(select(Post).where(Post.status == "scheduled", Post.scheduled_at > datetime.utcnow())).all():
        schedule_post(session, post)


def cancel_post_job(post_id: int):
    sched = start_scheduler()
    job_id = f"post_{post_id}"
    try:
        sched.remove_job(job_id)
    except Exception:
        pass
