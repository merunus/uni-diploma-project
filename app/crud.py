from sqlalchemy.orm import Session
from app.models import Word, UserProgress

def get_words_by_difficulty(db: Session, difficulty: str):
    return db.query(Word).filter(Word.difficulty == difficulty).all()

def update_user_progress(db: Session, user_id: int, word_id: int, known: bool):
    progress = UserProgress(user_id=user_id, word_id=word_id, known=known)
    db.add(progress)
    db.commit()
    return progress

def get_user_progress(db: Session, user_id: int):
    return db.query(UserProgress).filter(UserProgress.user_id == user_id).all()

def get_user_progress(db: Session, user_id: int):
    return db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
