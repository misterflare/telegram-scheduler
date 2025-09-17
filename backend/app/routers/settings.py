from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import BaseModel

from ..database import get_session
from ..models import User, AppSettings
from ..schemas import SettingsRead, SettingsUpdate, PasswordChange, Token
from ..auth import create_access_token, verify_password, get_password_hash
from ..deps import auth_required
from ..config import settings as env
from ..telegram_client import send_post
from ..utils.settings_migration import ensure_timezone_column

router = APIRouter(prefix="/settings", tags=["settings"])

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = await create_access_token(sub=user.username)
    return Token(access_token=token)


def _get_settings_row(session: Session) -> AppSettings:
    ensure_timezone_column(session)
    settings_row = session.exec(select(AppSettings)).first()
    if not settings_row:
        settings_row = AppSettings(
            id=1,
            bot_token=env.TELEGRAM_BOT_TOKEN,
            channel_id=env.TELEGRAM_CHANNEL_ID,
            timezone=env.TZ or "UTC",
        )
        session.add(settings_row)
        session.commit()
        session.refresh(settings_row)
    return settings_row


def _validate_timezone(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    if not trimmed:
        return None
    try:
        ZoneInfo(trimmed)
    except ZoneInfoNotFoundError:
        raise HTTPException(400, "Неизвестная тайм-зона. Используйте название из базы IANA, например Europe/Moscow")
    return trimmed


@router.get("/", response_model=SettingsRead)
def get_settings(session: Session = Depends(get_session), user=Depends(auth_required)):
    settings_row = _get_settings_row(session)
    return SettingsRead(
        bot_token="*** set ***" if settings_row.bot_token else None,
        channel_id=settings_row.channel_id,
        timezone=settings_row.timezone,
    )


@router.put("/", response_model=SettingsRead)
def update_settings(data: SettingsUpdate, session: Session = Depends(get_session), user=Depends(auth_required)):
    settings_row = _get_settings_row(session)

    if data.bot_token is not None:
        settings_row.bot_token = data.bot_token
        from ..telegram_client import _bot
        _bot = None  # force reinit

    if data.channel_id is not None:
        settings_row.channel_id = data.channel_id

    tz_changed = False
    if data.timezone is not None:
        new_tz = _validate_timezone(data.timezone)
        if settings_row.timezone != new_tz:
            settings_row.timezone = new_tz
            tz_changed = True

    session.add(settings_row)
    session.commit()
    session.refresh(settings_row)

    if tz_changed:
        from ..scheduler import bootstrap_pending

        bootstrap_pending(session)

    return SettingsRead(
        bot_token="*** set ***" if settings_row.bot_token else None,
        channel_id=settings_row.channel_id,
        timezone=settings_row.timezone,
    )


@router.post("/password")
def change_password(body: PasswordChange, session: Session = Depends(get_session), user=Depends(auth_required)):
    if body.new_password != body.new_password_confirm:
        raise HTTPException(400, "Password confirmation does not match")
    u = session.exec(select(User).where(User.username == user.username)).first()
    if not verify_password(body.old_password, u.password_hash):
        raise HTTPException(400, "Old password is incorrect")
    u.password_hash = get_password_hash(body.new_password)
    session.add(u)
    session.commit()
    return {"ok": True}


class TestPostBody(BaseModel):
    text: str | None = None


@router.post("/test")
async def test_post(body: TestPostBody, session: Session = Depends(get_session), user=Depends(auth_required)):
    settings_row = _get_settings_row(session)
    token = settings_row.bot_token or env.TELEGRAM_BOT_TOKEN
    channel = settings_row.channel_id or env.TELEGRAM_CHANNEL_ID
    if not token:
        raise HTTPException(400, "Токен бота не задан. Проверьте настройки.")
    if not channel:
        raise HTTPException(400, "ID канала/чата не задан. Проверьте настройки.")
    text = body.text or "Тестовая публикация из Telegram Scheduler"
    try:
        await send_post(text, None, None, channel, token=token)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Не удалось отправить тест: {str(e)[:300]}")
