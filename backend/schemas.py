
from pydantic import BaseModel
import datetime

class ExerciseBase(BaseModel):
    exercise_type: str
    question: str
    answer: str

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    lesson_id: int

    class Config:
        orm_mode = True

class LessonCreate(BaseModel):
    title: str

class Lesson(BaseModel):
    id: int
    title: str
    exercises: list[Exercise] = []

    class Config:
        orm_mode = True

class ProgressBase(BaseModel):
    exercise_id: int

class ProgressCreate(ProgressBase):
    pass

class Progress(ProgressBase):
    id: int
    user_id: int
    completed_at: datetime.datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    progress: list[Progress] = []

    class Config:
        orm_mode = True
