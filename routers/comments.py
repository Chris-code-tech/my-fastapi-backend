from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import models, schemas
from database import SessionLocal


router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
        
# ---------------------------
# Create Comment or Reply 
# ---------------------------
@router.post("/comments", response_model=schemas.CommentOut)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Get username for response
    user = db.query(models.User).filter(models.User.id == db_comment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.CommentOut(
        id=db_comment.id,
        username=user.username,
        post_id=db_comment.post_id,
        content=db_comment.content,
        parent_comment_id=db_comment.parent_comment_id,
        replying_to_comment_id=db_comment.replying_to_comment_id, # ← NEW
        created_at=db_comment.created_at,
    )

# ---------------------------
# Get All Comments + Replies
# ---------------------------
@router.get("/comments/{post_id}", response_model=list[schemas.CommentOut])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    Comment = models.Comment
    User = models.User

    # Get all comments with creator and replied-to user
    comments = (
        db.query(Comment)
        .options(joinedload(Comment.creator))
        .filter(Comment.post_id == post_id)
        .all()
    )

    result = []
    for c in comments:
        # Get the user being replied to (if any)
        replying_to_username = None
        
        if c.replying_to_comment_id:
            replied_comment = db.query(Comment).filter(Comment.id == c.replying_to_comment_id).first()
            
            if replied_comment and replied_comment.replying_to_comment_id:
                # Only get username if we're replying to a reply
                replied_user = db.query(User).filter(User.id == replied_comment.user_id).first()
                if replied_user:
                    replying_to_username = replied_user.username
                    
        result.append(
            schemas.CommentOut(
                id=c.id,
                username=c.creator.username if c.creator else "unknown",
                post_id=c.post_id,
                content=c.content,
                parent_comment_id=c.parent_comment_id,
                replying_to_comment_id=c.replying_to_comment_id,
                created_at=c.created_at,
                replying_to_username=replying_to_username # new field!
            )
        )
    return result
