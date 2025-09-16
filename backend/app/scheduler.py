from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
from sqlmodel import Session, select
from .database import engine
from .models import Post
from .services.posting import publish_post
import asyncio

scheduler: BackgroundScheduler | None = None

def start_scheduler():
    global scheduler
    if scheduler:
        return scheduler
    scheduler = BackgroundScheduler(jobstores={"default": SQLAlchemyJobStore(engine=engine)})
    scheduler.start()
    return scheduler

def schedule_post(session: Session, post: Post):
    sched = start_scheduler()
    job_id = f"post_{post.id}"
    # Remove any existing job
    try:
        sched.remove_job(job_id)
    except Exception:
        pass

    if post.status == "scheduled" and post.scheduled_at > datetime.utcnow():
        sched.add_job(lambda: asyncio.run(publish_post(session, post.id)), trigger="date", run_date=post.scheduled_at, id=job_id, replace_existing=True)

def bootstrap_pending(session: Session):
    # Schedule all future scheduled posts on startup
    for post in session.exec(select(Post).where(Post.status == "scheduled", Post.scheduled_at > datetime.utcnow())).all():
        schedule_post(session, post)
