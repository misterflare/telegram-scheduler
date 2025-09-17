from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select

from ..models import AppSettings


def ensure_timezone_column(session: Session) -> None:
    try:
        session.exec(select(AppSettings.timezone)).first()
    except OperationalError as exc:
        message = str(exc)
        if "no such column" in message and "appsettings.timezone" in message:
            session.exec(text("ALTER TABLE appsettings ADD COLUMN timezone VARCHAR(64)"))
            session.commit()
        else:
            raise
