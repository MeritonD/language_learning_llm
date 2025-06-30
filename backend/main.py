from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from . import auth, models, schemas, users, lessons, exercises, llm, progress
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = users.get_user_by_username(db, username=token_data)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = users.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = users.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return users.create_user(db=db, user=user)


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@app.post("/lessons/", response_model=schemas.Lesson)
def create_lesson(lesson: schemas.LessonCreate, db: Session = Depends(get_db)):
    return lessons.create_lesson(db=db, lesson=lesson)


@app.get("/lessons/", response_model=list[schemas.Lesson])
def read_lessons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_lessons = lessons.get_lessons(db, skip=skip, limit=limit)
    return db_lessons


@app.get("/lessons/{lesson_id}", response_model=schemas.Lesson)
def read_lesson(lesson_id: int, db: Session = Depends(get_db)):
    db_lesson = lessons.get_lesson(db, lesson_id=lesson_id)
    if db_lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return db_lesson


@app.post("/lessons/{lesson_id}/exercises/", response_model=schemas.Exercise)
def create_exercise_for_lesson(
    lesson_id: int, exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)
):
    return exercises.create_exercise(db=db, exercise=exercise, lesson_id=lesson_id)


@app.get("/lessons/{lesson_id}/exercises/", response_model=list[schemas.Exercise])
def read_exercises_for_lesson(
    lesson_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    db_exercises = exercises.get_exercises_by_lesson(
        db, lesson_id=lesson_id, skip=skip, limit=limit
    )
    return db_exercises

@app.post("/exercises/{exercise_id}/feedback")
def get_exercise_feedback(exercise_id: int, answer: str, db: Session = Depends(get_db)):
    db_exercise = exercises.get_exercise(db, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    prompt = f"Question: {db_exercise.question}\nAnswer: {answer}\nIs the answer correct? Provide feedback."
    feedback = llm.get_llm_feedback(prompt)
    return {"feedback": feedback}

@app.post("/progress/", response_model=schemas.Progress)
def create_progress_for_user(
    exercise_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return progress.create_progress(db=db, user_id=current_user.id, exercise_id=exercise_id)


@app.get("/progress/", response_model=list[schemas.Progress])
def read_progress_for_user(
    current_user: schemas.User = Depends(get_current_user), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    db_progress = progress.get_progress(db, user_id=current_user.id, skip=skip, limit=limit)
    return db_progress