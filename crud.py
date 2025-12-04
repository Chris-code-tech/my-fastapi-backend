from sqlalchemy.orm import Session, joinedload
import models, schemas
from schemas import UserCreate, PostCreate
from models import User, Post

def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id ==user_id).first()



# For Create a post
def create_post(db: Session, post: PostCreate):
    db_post = Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Get Posts
def get_posts(db: Session):
    return db.query(Post).options(joinedload(Post.user)).all()

# For TrackScreen
def get_tracks(db: Session):
    return (
        db.query(models.TrackEntry)
        .order_by(models.TrackEntry.created_at.desc())
        .all()
    )

def create_track(db: Session, entry: schemas.TrackCreate):
    db_entry = models.TrackEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    print("DBG entry dict =>", db_entry.__dict__)
    return db_entry