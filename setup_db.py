from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import Word, User
from passlib.hash import bcrypt


# Створення таблиць у базі даних
def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("✅ База даних створена!")


# Функція для додавання початкових слів
def seed_database():
    db: Session = SessionLocal()

    words = [
        # Easy words
        {"word": "apple", "translation": "яблуко", "difficulty": "easy"},
        {"word": "banana", "translation": "банан", "difficulty": "easy"},
        {"word": "dog", "translation": "собака", "difficulty": "easy"},
        {"word": "cat", "translation": "кіт", "difficulty": "easy"},
        {"word": "house", "translation": "будинок", "difficulty": "easy"},
        {"word": "book", "translation": "книга", "difficulty": "easy"},
        {"word": "tree", "translation": "дерево", "difficulty": "easy"},
        {"word": "sun", "translation": "сонце", "difficulty": "easy"},
        {"word": "moon", "translation": "місяць", "difficulty": "easy"},
        {"word": "star", "translation": "зірка", "difficulty": "easy"},
        {"word": "water", "translation": "вода", "difficulty": "easy"},
        {"word": "fire", "translation": "вогонь", "difficulty": "easy"},
        {"word": "earth", "translation": "земля", "difficulty": "easy"},
        {"word": "air", "translation": "повітря", "difficulty": "easy"},
        {"word": "sky", "translation": "небо", "difficulty": "easy"},
        
        # Medium words
        {"word": "elephant", "translation": "слон", "difficulty": "medium"},
        {"word": "computer", "translation": "комп'ютер", "difficulty": "medium"},
        {"word": "language", "translation": "мова", "difficulty": "medium"},
        {"word": "weather", "translation": "погода", "difficulty": "medium"},
        {"word": "garden", "translation": "сад", "difficulty": "medium"},
        {"word": "kitchen", "translation": "кухня", "difficulty": "medium"},
        {"word": "bicycle", "translation": "велосипед", "difficulty": "medium"},
        {"word": "telephone", "translation": "телефон", "difficulty": "medium"},
        {"word": "hospital", "translation": "лікарня", "difficulty": "medium"},
        {"word": "restaurant", "translation": "ресторан", "difficulty": "medium"},
        {"word": "university", "translation": "університет", "difficulty": "medium"},
        {"word": "dictionary", "translation": "словник", "difficulty": "medium"},
        {"word": "newspaper", "translation": "газета", "difficulty": "medium"},
        {"word": "magazine", "translation": "журнал", "difficulty": "medium"},
        {"word": "calendar", "translation": "календар", "difficulty": "medium"},
        
        # Hard words
        {"word": "architecture", "translation": "архітектура", "difficulty": "hard"},
        {"word": "philosophy", "translation": "філософія", "difficulty": "hard"},
        {"word": "democracy", "translation": "демократія", "difficulty": "hard"},
        {"word": "technology", "translation": "технологія", "difficulty": "hard"},
        {"word": "environment", "translation": "довкілля", "difficulty": "hard"},
        {"word": "government", "translation": "уряд", "difficulty": "hard"},
        {"word": "education", "translation": "освіта", "difficulty": "hard"},
        {"word": "experience", "translation": "досвід", "difficulty": "hard"},
        {"word": "knowledge", "translation": "знання", "difficulty": "hard"},
        {"word": "development", "translation": "розвиток", "difficulty": "hard"},
        {"word": "management", "translation": "управління", "difficulty": "hard"},
        {"word": "opportunity", "translation": "можливість", "difficulty": "hard"},
        {"word": "responsibility", "translation": "відповідальність", "difficulty": "hard"},
        {"word": "sustainability", "translation": "стійкість", "difficulty": "hard"},
        {"word": "infrastructure", "translation": "інфраструктура", "difficulty": "hard"}
    ]

    for word in words:
        existing_word = db.query(Word).filter_by(word=word["word"]).first()
        if not existing_word:
            new_word = Word(**word)
            db.add(new_word)

    db.commit()
    db.close()
    print("✅ База даних успішно наповнена словами!")


# Функція для створення адміністратора
def create_admin():
    db = SessionLocal()

    admin_user = db.query(User).filter_by(username="admin").first()
    if not admin_user:
        admin = User(username="admin", hashed_password=bcrypt.hash("admin123"), role="admin")
        db.add(admin)
        db.commit()
        print("✅ Адміністратор створений: Логін - admin, Пароль - admin123")

    db.close()


# Головний запуск ініціалізації бази
if __name__ == "__main__":
    initialize_database()
    create_admin()
    seed_database()
