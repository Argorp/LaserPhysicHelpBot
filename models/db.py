from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import Base

engine = create_engine('sqlite:///db_dir/telegram_bot.db')
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()