from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from models.user import Base


class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    text = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="user_feedback")
    def __repr__(self):
        return f"<Feedback({self.user_id}, {self.created_at})>"