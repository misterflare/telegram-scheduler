import os
import pytz
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from .config import settings
from .database import init_db, engine
from .models import User, AppSettings
from .auth import get_password_hash
from .scheduler import start_scheduler, bootstrap_pending
from .routers import posts, files, settings as settings_router

app = FastAPI(title="Telegram Scheduler (single-user)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_db()
    # init admin
    with Session(engine) as session:
        u = session.exec(select(User).where(User.username == settings.ADMIN_USERNAME)).first()
        if not u:
            u = User(username=settings.ADMIN_USERNAME, password_hash=get_password_hash(settings.ADMIN_PASSWORD))
            session.add(u); session.commit()
        s = session.exec(select(AppSettings)).first()
        if not s:
            s = AppSettings(id=1, bot_token=settings.TELEGRAM_BOT_TOKEN, channel_id=settings.TELEGRAM_CHANNEL_ID)
            session.add(s); session.commit()
        start_scheduler()
        bootstrap_pending(session)

app.include_router(settings_router.auth_router)
app.include_router(settings_router.router)
app.include_router(files.router)
app.include_router(posts.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
