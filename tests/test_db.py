from app.database import SessionLocal
from app.models import Word

def test_database_connection():
    db = SessionLocal()
    word = Word(word="Test", translation="Тест", difficulty="easy")
    db.add(word)
    db.commit()
    result = db.query(Word).filter_by(word="Test").first()
    assert result is not None
    db.delete(result)
    db.commit()
    db.close()
