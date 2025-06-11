from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class WordBase(BaseModel):
    word: str
    translation: str
    difficulty: str

class WordCreate(WordBase):
    pass

class Word(WordBase):
    id: int

    class Config:
        from_attributes = True

class ProgressBase(BaseModel):
    user_id: int
    word_id: int
    status: str

class ProgressCreate(ProgressBase):
    pass

class Progress(ProgressBase):
    id: int

    class Config:
        from_attributes = True

class QuizResultCreate(BaseModel):
    user_id: int
    total_questions: int
    correct_answers: int
    wrong_answers: int

class QuizResult(QuizResultCreate):
    id: int
    date: datetime

    class Config:
        from_attributes = True
