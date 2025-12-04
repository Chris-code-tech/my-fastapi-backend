from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone


def _dt_encoder(v: datetime):
    if v is None:
            return None
    # If naive, treat it as UTC (safe default if your DB uses UTC)
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    # Convert to UTC and return ISO with Z
    return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

# Posts
class PostCreate(BaseModel):
    user_id: int
    title: Optional[str] = None
    content: str
    tab: str


class PostOut(BaseModel):
    id: int
    title: Optional[str] = None
    content: str
    tab: str
    creator: str
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = { datetime: _dt_encoder }


class SavedPostOut(BaseModel):
    id: int
    title: Optional[str] = None
    content: str
    tab: str
    creator: str
    created_at: datetime
    saved: bool

    class Config:
        orm_mode = True
        json_encoders = { datetime: _dt_encoder }


class MyPostOut(BaseModel):
    id: int
    title: Optional[str] = None
    content: str
    tab: str
    created_at: datetime
    comments_number: int

    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    content: str
    user_id: int
    post_id: int
    parent_comment_id: Optional[int] = None
    replying_to_comment_id: Optional[int] = None

class ReplyOut(BaseModel):
    id: int
    content: str
    username: str
    created_at: datetime

    class Config:
        orm_mode = True


class CommentOut(BaseModel):
    id: int
    content: str
    username: str
    post_id: int
    parent_comment_id: Optional[int] = None
    replying_to_comment_id: Optional[int] = None
    replying_to_username: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class SavePostRequest(BaseModel):
    user_id: int
    post_id: int



class TrackBase(BaseModel):
    type: str
    name: str
    additionalInfo: str
    description: List[str]

class TrackCreate(TrackBase):
    type: Optional[str] = None
    name: Optional[str] = None
    additionalInfo: Optional[str] = None
    description: Optional[List[str]] = None

class TrackOut(TrackBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True