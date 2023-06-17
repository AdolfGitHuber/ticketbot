from sqlalchemy import (
    Column, 
    Integer,
    String,
    ForeignKey
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

    color_id = Column(Integer, ForeignKey("color.id"), unique=True)
    color = relationship("Color", back_populates="user_clr")
    tickets = relationship("Ticket", back_populates="author_id")
    departments = relationship("UserDepartment", back_populates="user")


    def __repr__(self):
        return (
            f"User(telegram_id={self.telegram_id!r}, "
            f"username={self.username!r}, "
            f"first_name={self.first_name!r}, "
            f"role={self.role!r})"
            )