from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, JSON
from database import Base




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    shared = Column(String)
 
    posts = relationship("Post", back_populates="creator", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="creator", cascade="all, delete-orphan")
    saved_posts = relationship("SavedPost", back_populates="user")



class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title= Column(String, nullable=True)
    content = Column(String, nullable=False)
    tab= Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), # Python-side default (tz-aware)
        server_default=func.now(), # DB-side default (depends on DB config)
        nullable=False,
    )
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="posts")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    replying_to_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    creator = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], foreign_keys=[parent_comment_id], backref="replies")
    replying_to = relationship("Comment", remote_side=[id], foreign_keys=[replying_to_comment_id])

class SavedPost(Base):
    __tablename__ = "saved_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    user = relationship("User", back_populates="saved_posts")
    post = relationship("Post")



class Share(Base):
    __tablename__ = "shares"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    shared_at = Column(DateTime(timezone=True), server_default=func.now())

# For TrackScreen
class TrackEntry(Base):
    __tablename__ = "track_entries"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    name = Column(String, index=True)
    additionalInfo = Column(String)
    description = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)