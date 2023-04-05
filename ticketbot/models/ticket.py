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

from ticketbot.models.base import Base
from ticketbot.models.enum.ticket_state import TicketState




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
    ticket_creation_date = Column(DateTime(timezone=True), server_default=func.now())
    state = Column(Enum(TicketState), default=TicketState.OPEN)
    

    author = Column(BigInteger, ForeignKey("user.telegram_id"))
    author_id = relationship("User", back_populates="tickets", lazy="selectin")
    department = Column(Integer, ForeignKey("department.id"))
    department_id = relationship("Department", back_populates="tickets", lazy="selectin")


    def __repr__(self):
        return (f"Ticket("
                f"id={self.ticket_id!r},\n"
                f"text={self.ticket_text!r},\n"
                f"creation_date={self.ticket_creation_date!r},\n"
                f"state={self.state!r})\n"
                f"author={self.author!r}\n"
                f"department={self.department!r}")