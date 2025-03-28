from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from models.reserve_bot import Base


class Reservations(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    status = Column(String)
    created_at = Column(
        DateTime(timezone=True), server_default=func.timezone("Asia/Tehran", func.now())
    )

    def __repr__(self):
        return f"room_id:'{self.room_id}', user_id:'{self.user_id}', date:'{self.date}', start:'{self.start_time}', end:'{self.end_time}', status:'{self.status}', created_at:'{self.created_at}'"
