from sqlalchemy import (
    Column, 
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Identity
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base




"""
ticket_id PRIMARY KEY, index
ticket_text TEXT NOT NULL
ticket_creation_date DATETIME NOT NULL
state TEXT
author FOREIGN KEY (user_id) REFERENCES User
"""
class Ticket(Base):
    __tablename__ = 'ticket'

    ticket_id = Column(
        BigInteger,
        Identity(always=True, cycle=False),
        primary_key=True
        )
    ticket_text = Column(String, nullable=False)
    creation_date = Column(DateTime(timezone=True), default=func.now())
    state = Column(String, default='open', nullable=False)
    

    author = Column(BigInteger, ForeignKey("user.telegram_id"))
    author_id = relationship("User", back_populates="tickets", lazy="selectin")
    department = Column(Integer, ForeignKey("department.id"))
    department_id = relationship("Department", back_populates="tickets", lazy="selectin")


    def __repr__(self):
        return (f"Ticket("
                f"id={self.ticket_id!r}, "
                f"text={self.ticket_text!r}, "
                f"creation_date={self.ticket_creation_date!r}, "
                f"state={self.state!r})")