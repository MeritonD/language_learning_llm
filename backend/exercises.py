
from sqlalchemy.orm import Session
from . import models, schemas

def get_exercise(db: Session, exercise_id: int):
    return db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()

def get_exercises_by_lesson(db: Session, lesson_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Exercise).filter(models.Exercise.lesson_id == lesson_id).offset(skip).limit(limit).all()

def create_exercise(db: Session, exercise: schemas.ExerciseCreate, lesson_id: int):
    db_exercise = models.Exercise(**exercise.dict(), lesson_id=lesson_id)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise
