from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas, crud
from models import TrackEntry
from schemas import TrackCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.TrackOut])
def read_tracks(db: Session = Depends(get_db)):
    return crud.get_tracks(db)


@router.post("/", response_model=schemas.TrackOut)
def add_track(entry: schemas.TrackCreate, db: Session = Depends(get_db)):
    return crud.create_track(db, entry)


@router.patch("/{track_id}")
def update_track(track_id: int, update_data: TrackCreate, db: Session = Depends(get_db)):
    track = db.query(TrackEntry).filter(TrackEntry.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(track, key, value)

    db.commit()
    db.refresh(track)
    return track

@router.delete("/{track_id}", status_code=204)
def delete_track(track_id: int, db: Session = Depends(get_db)):
    track = db.query(models.TrackEntry).filter(models.TrackEntry.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    db.delete(track)
    db.commit()
    return