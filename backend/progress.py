
from sqlalchemy.orm import Session
from . import models, schemas

def get_progress(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Progress).filter(models.Progress.user_id == user_id).offset(skip).limit(limit).all()

def create_progress(db: Session, user_id: int, exercise_id: int):
    db_progress = models.Progress(user_id=user_id, exercise_id=exercise_id)
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress
