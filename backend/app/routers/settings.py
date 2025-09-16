from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..database import get_session
from ..models import User, AppSettings
from ..schemas import SettingsRead, SettingsUpdate, PasswordChange, Token
from ..auth import create_access_token, verify_password, get_password_hash
from ..deps import auth_required
from ..config import settings as env

router = APIRouter(prefix="/settings", tags=["settings"])

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = await create_access_token(sub=user.username)
    return Token(access_token=token)

@router.get("/", response_model=SettingsRead)
def get_settings(session: Session = Depends(get_session), user = Depends(auth_required)):
    s = session.exec(select(AppSettings)).first()
    if not s:
        s = AppSettings(id=1, bot_token=env.TELEGRAM_BOT_TOKEN, channel_id=env.TELEGRAM_CHANNEL_ID)
        session.add(s); session.commit(); session.refresh(s)
    return SettingsRead(bot_token=bool(s.bot_token) and "*** set ***" or None, channel_id=s.channel_id)

@router.put("/", response_model=SettingsRead)
def update_settings(data: SettingsUpdate, session: Session = Depends(get_session), user = Depends(auth_required)):
    s = session.exec(select(AppSettings)).first()
    if not s:
        s = AppSettings(id=1)
    if data.bot_token is not None:
        s.bot_token = data.bot_token
        # also refresh runtime bot token
        from ..telegram_client import _bot
        _bot = None  # force reinit
    if data.channel_id is not None:
        s.channel_id = data.channel_id
    session.add(s); session.commit(); session.refresh(s)
    return SettingsRead(bot_token="*** set ***" if s.bot_token else None, channel_id=s.channel_id)

@router.post("/password")
def change_password(body: PasswordChange, session: Session = Depends(get_session), user = Depends(auth_required)):
    if body.new_password != body.new_password_confirm:
        raise HTTPException(400, "Password confirmation does not match")
    u = session.exec(select(User).where(User.username == user.username)).first()
    if not verify_password(body.old_password, u.password_hash):
        raise HTTPException(400, "Old password is incorrect")
    u.password_hash = get_password_hash(body.new_password)
    session.add(u); session.commit()
    return {"ok": True}
