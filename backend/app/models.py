from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str

class AppSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=1, primary_key=True)
    bot_token: Optional[str] = None
    channel_id: Optional[str] = None

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: Optional[str] = None
    buttons: Optional[List[dict]] = Field(sa_column=Column(JSON), default=None)
    media: Optional[List[dict]] = Field(sa_column=Column(JSON), default=None)  # [{type:"photo|video|document", path:"/data/uploads/.."}]
    scheduled_at: datetime
    status: str = Field(default="scheduled")  # scheduled|posted|failed|canceled
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
