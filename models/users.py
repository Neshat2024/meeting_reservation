from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.reserve_bot import Base
from models.rooms import Rooms
from models.reservations import Reservations


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True)
    username = Column(String, unique=True)
    name = Column(String, unique=True)
    role = Column(String)
    command = Column(String)
    charge = Column(Integer, default=0)
    reservation = relationship(Reservations, backref="main_user")
    room = relationship(Rooms, backref="admin")
    color = Column(String)
    language = Column(String, default="fa")
    created_at = Column(
        DateTime(timezone=True), server_default=func.timezone("Asia/Tehran", func.now())
    )

    def __repr__(self):
        return f"username:'{self.username}', name:'{self.name}', reservation:'{self.reservation}', created_at:'{self.created_at}'"
