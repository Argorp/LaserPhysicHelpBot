from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    registration_date = Column(DateTime, default=datetime.utcnow)
    request_count = Column(Integer, default=0)
    last_request = Column(DateTime)
    is_banned = Column(Boolean, default=False)
    user_feedback = relationship("Feedback", uselist=False, back_populates="user")

    def __repr__(self):
        return f"<User({self.user_id}, {self.username})>"