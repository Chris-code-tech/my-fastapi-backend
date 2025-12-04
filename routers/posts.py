from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal, engine
import models, schemas
from models import Post, User, Comment, SavedPost
from schemas import PostOut, CommentOut, ReplyOut, PostCreate, MyPostOut, SavedPostOut
from typing import List, Optional
from fastapi.responses import JSONResponse


router = APIRouter() # Dependency

def get_db(): 
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Query

@router.get("/posts", response_model=list[SavedPostOut])
def get_posts(
    user_id: Optional[int] = Query(None),
    tab: Optional[str] = None,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Post).options(joinedload(Post.creator))

    if tab:
        query = query.filter(Post.tab == tab)

    posts = query.offset(skip).all()

    # If user_id is None → return saved=False for everything
    if user_id is not None:
        saved = db.query(SavedPost.post_id).filter(
            SavedPost.user_id == user_id
        ).all()
        saved_ids = {row[0] for row in saved}
    else:
        saved_ids = set()

    return [
        SavedPostOut(
            id=post.id,
            title=post.title,
            content=post.content,
            tab=post.tab,
            creator=post.creator.username,
            created_at=post.created_at,
            saved=(post.id in saved_ids)
        )
        for post in posts
    ]


# Get a single post
@router.get("/singlepost/{post_id}", response_model=SavedPostOut)
def get_post(
    post_id: int,
    user_id: Optional[int] = Query(None),  # Optional query param
    db: Session = Depends(get_db)
):
    # Fetch the post
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if user saved it (only if user_id exists)
    if user_id is not None:
        saved = db.query(models.SavedPost.post_id).filter(
            models.SavedPost.user_id == user_id,
            models.SavedPost.post_id == post_id
        ).all()
        saved_ids = {row[0] for row in saved}
        is_saved = post_id in saved_ids
    else:
        is_saved = False

    return SavedPostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        tab=post.tab,
        created_at=post.created_at,
        creator=post.creator.username if post.creator else "Unknown",
        saved=is_saved
    )

# Post something
@router.post("/newpost", response_model=PostOut)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == post.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_post = Post(
        title=post.title,
        content=post.content,
        tab=post.tab,
        creator=user # this sets the relationship
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return PostOut(
        id=new_post.id,
        title=new_post.title,
        content=new_post.content,
        tab=new_post.tab,
        creator=user.username,
        created_at=new_post.created_at,
    )

# Get my posts
@router.get("/myposts/{user_id}", response_model=List[schemas.MyPostOut])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    queried_posts = db.query(Post).filter(Post.user_id == user_id).all()

    my_posts = []
    for post in queried_posts:
        post_id = post.id

        comments = (
            db.query(Comment)
            .filter(Comment.post_id == post_id)
            .all()
        )
        my_posts.append(
            MyPostOut(
                title=post.title,
                content=post.content,
                id=post.id,
                created_at=post.created_at,
                tab=post.tab,
                comments_number=len(comments)
            )
        )
    return my_posts


# Share a post
@router.post("/share")
def share_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    share = models.Share(post_id=post_id, user_id=user_id)
    db.add(share)
    db.commit()
    return {"message": "Shared recorded"}


# Save a post
@router.post("/posts/save")
def save_or_unsave_post(data: schemas.SavePostRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    post = db.query(models.Post).filter(models.Post.id == data.post_id).first()

    if not user or not post:
        raise HTTPException(status_code=404, detail="User or Post not found")

    # Check if this post is already saved
    existing = db.query(models.SavedPost).filter_by(user_id=data.user_id, post_id=data.post_id).first()
    print("Existing:", existing)
    if existing:
        # Unsave
        db.delete(existing)
        db.commit()
        return {"message": "Post unsaved"}
    else:
        # Save
        new_save = models.SavedPost(user_id=data.user_id, post_id=data.post_id)
        db.add(new_save)
        db.commit()
        return {"message": "Post saved"}
    
# Get saved posts
@router.get("/users/{user_id}/saved-posts")
def get_saved_posts(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    saved_entries = db.query(models.SavedPost).filter(models.SavedPost.user_id == user_id).all()

    posts = [entry.post for entry in saved_entries if entry.post]

    return [
        PostOut(
            id= post.id,
            title=post.title,
            content= post.content,
            tab= post.tab,
            creator= post.creator.username,
            created_at= post.created_at,
        )
        for post in posts
        
    ]

    

# Delete post
@router.delete("/posts/delete/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    print("Post to delete:", post)
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}