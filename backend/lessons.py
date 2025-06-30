
from sqlalchemy.orm import Session
from . import models, schemas

def get_lesson(db: Session, lesson_id: int):
    return db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()

def get_lessons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Lesson).offset(skip).limit(limit).all()

def create_lesson(db: Session, lesson: schemas.LessonCreate):
    db_lesson = models.Lesson(title=lesson.title)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson
