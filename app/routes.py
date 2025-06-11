from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from passlib.hash import bcrypt
from app.crud import get_words_by_difficulty, update_user_progress, get_user_progress
from app.schemas import ProgressCreate, UserCreate
from app.models import UserProgress
from pydantic import BaseModel
from app.models import Word, User, QuizResult
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"  # Replace with a secure key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class NewWordSchema(BaseModel):
    word: str
    translation: str
    difficulty: str


class UserSchema(BaseModel):
    username: str
    password: str

class ProgressSchema(BaseModel):
    user_id: int
    word_id: int
    known: bool

class QuizResultCreate(BaseModel):
    user_id: int
    total_questions: int
    correct_answers: int
    wrong_answers: int

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        print(f"Received registration request for username: {user.username}")  # Debug log
        
        # Check if user exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="❌ Користувач вже існує")

        # Create new user
        hashed_password = pwd_context.hash(user.password)
        new_user = User(
            username=user.username,
            hashed_password=hashed_password,
            role="user"
        )
        
        # Save to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"User registered successfully with ID: {new_user.id}")  # Debug log
        return {"message": "✅ Реєстрація успішна"}
        
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug log
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка реєстрації: {str(e)}")


@router.post("/login/")
def login(user_data: UserSchema, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.username == user_data.username).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Невірний логін або пароль")
        
        if not pwd_context.verify(user_data.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Невірний логін або пароль")
        
        access_token = create_access_token(data={"sub": user_data.username})
        print(f"User logged in - ID: {db_user.id}, Username: {db_user.username}")  # Debug print
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": db_user.id,
            "role": db_user.role
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/words/add")
def add_word(word_data: NewWordSchema, db: Session = Depends(get_db)):
    try:
        new_word = Word(
            word=word_data.word,
            translation=word_data.translation,
            difficulty=word_data.difficulty
        )
        db.add(new_word)
        db.commit()
        return {"message": "Слово додано успішно!"}
    except Exception as e:
        db.rollback()  # Відкат змін у разі помилки
        raise HTTPException(status_code=500, detail=f"Помилка сервера: {str(e)}")

@router.get("/words/{difficulty}")
def get_words(difficulty: str, db: Session = Depends(get_db)):
    return get_words_by_difficulty(db, difficulty)


@router.post("/progress/")
def update_progress(progress_list: list[ProgressSchema], db: Session = Depends(get_db)):
    for progress in progress_list:
        existing_entry = db.query(UserProgress).filter(
            UserProgress.user_id == progress.user_id,
            UserProgress.word_id == progress.word_id
        ).first()

        if existing_entry:
            existing_entry.known = progress.known
        else:
            new_progress = UserProgress(
                user_id=progress.user_id,
                word_id=progress.word_id,
                known=progress.known
            )
            db.add(new_progress)

    db.commit()
    return {"message": "Прогрес оновлено"}


@router.get("/progress/{user_id}")
def get_progress(user_id: int, db: Session = Depends(get_db)):
    progress_entries = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()

    if not progress_entries:
        return []

    return [{"word_id": entry.word_id, "known": entry.known} for entry in progress_entries]

@router.get("/stats/{username}")
def get_user_stats(username: str, db: Session = Depends(get_db)):
    try:
        print(f"Getting stats for username: {username}")  # Debug print
        
        # Знаходимо користувача
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User not found: {username}")  # Debug print
            return []
        
        print(f"Found user with ID: {user.id}")  # Debug print
        
        # Отримуємо результати вікторин
        quiz_results = db.query(QuizResult).filter(QuizResult.user_id == user.id).all()
        print(f"Found {len(quiz_results)} quiz results")  # Debug print
        
        stats = []
        for result in quiz_results:
            stats.append({
                "id": result.id,
                "date": result.date.isoformat(),
                "total_questions": result.total_questions,
                "correct_answers": result.correct_answers,
                "wrong_answers": result.wrong_answers
            })
        
        return stats
    except Exception as e:
        print(f"Error getting stats: {str(e)}")  # Debug print
        return []

# Додаємо тестовий ендпоінт для перевірки
@router.get("/test-stats/{username}")
def test_user_stats(username: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return {"error": "User not found"}
        return {"user_id": user.id, "username": user.username}
    except Exception as e:
        return {"error": str(e)}

@router.post("/quiz-results/")
def create_quiz_result(quiz_result: QuizResultCreate, db: Session = Depends(get_db)):
    try:
        print(f"Received quiz result for user_id: {quiz_result.user_id}")  # Debug print
        # Перевіряємо чи існує користувач
        user = db.query(User).filter(User.id == quiz_result.user_id).first()
        if not user:
            print(f"User not found with ID: {quiz_result.user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"Found user: {user.username}")  # Debug print
        
        # Створюємо новий запис результату
        db_quiz_result = QuizResult(
            user_id=quiz_result.user_id,
            total_questions=quiz_result.total_questions,
            correct_answers=quiz_result.correct_answers,
            wrong_answers=quiz_result.wrong_answers,
            date=datetime.now()
        )
        
        # Зберігаємо в базу даних
        db.add(db_quiz_result)
        db.commit()
        db.refresh(db_quiz_result)
        
        print(f"Quiz result saved with ID: {db_quiz_result.id}")  # Debug print
        
        return {
            "id": db_quiz_result.id,
            "date": db_quiz_result.date.isoformat(),
            "total_questions": db_quiz_result.total_questions,
            "correct_answers": db_quiz_result.correct_answers,
            "wrong_answers": db_quiz_result.wrong_answers
        }
    except Exception as e:
        db.rollback()
        print(f"Error saving quiz result: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

