from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

class Button(BaseModel):
    title: str
    url: str

class MediaItem(BaseModel):
    type: str  # photo|video|document
    path: str

class PostCreate(BaseModel):
    text: Optional[str] = None
    buttons: Optional[List[Button]] = None
    media: Optional[List[MediaItem]] = None
    scheduled_at: datetime

class PostRead(PostCreate):
    id: int
    status: str
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class PostUpdate(BaseModel):
    text: Optional[str] = None
    buttons: Optional[List[Button]] = None
    media: Optional[List[MediaItem]] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None

class SettingsRead(BaseModel):
    bot_token: Optional[str] = None
    channel_id: Optional[str] = None

class SettingsUpdate(BaseModel):
    bot_token: Optional[str] = None
    channel_id: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    new_password_confirm: str
