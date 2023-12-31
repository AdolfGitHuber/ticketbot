from sqlalchemy import (
    Column, 
    Integer,
    String,
    Enum
)
from sqlalchemy.orm import relationship

from . import Base


"""
user_id PRIMARY KEY
username TEXT NOT NULL
role TEXT NOT NULL
"""
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    username = Column(String(32), nullable=True)
    first_name = Column(String(32), nullable=True)
    role = Column(String, default='unregistered')
    color = Column(String)

    tickets = relationship("Ticket", back_populates="author_id", lazy="selectin")
    departments = relationship("UserDepartment", back_populates="user", lazy="selectin")


    def __repr__(self):
        return (
            f"User(telegram_id={self.telegram_id!r}\n"
            f"username={self.username!r}\n"
            f"first_name={self.first_name!r}\n"
            f"role={self.role!r})\n"
            f"tickets={self.tickets!r}"
            )