from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from sqlmodel import Session, select

from ..models import AppSettings
from ..config import settings as env


def resolve_timezone_name(session: Session) -> str:
    tz_name = env.TZ or "UTC"
    settings_row = session.exec(select(AppSettings)).first()
    if settings_row and settings_row.timezone:
        tz_name = settings_row.timezone
    return tz_name


def resolve_timezone(session: Session) -> ZoneInfo:
    tz_name = resolve_timezone_name(session)
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")
