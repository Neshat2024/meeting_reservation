from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from models.reserve_bot import Base


class Rooms(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    capacity = Column(Integer)
    facilities = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('Asia/Tehran', func.now()))

    def __repr__(self):
        return f"room_id:'{self.id}', room_name:'{self.name}', admin_id:'{self.user_id}'"
