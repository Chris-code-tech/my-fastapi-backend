from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from routers import track, posts, comments
import models, schemas
from database import SessionLocal, engine
from schemas import UserCreate
from crud import create_user
from typing import List
from models import Post, Base


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@app.post("/login")
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if user.password != user_data.password:
        raise HTTPException(status_code=400, detail= "Invalid username or password")
    return {"id": user.id, "username": user.username}

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)



app.include_router(track.router, prefix="/track", tags=["Track"])
app.include_router(posts.router)
app.include_router(comments.router)



