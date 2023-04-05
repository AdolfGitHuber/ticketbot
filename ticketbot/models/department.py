from sqlalchemy import (
    Column, 
    Integer,
    String
)
from sqlalchemy.orm import relationship

from ticketbot.models.base import Base



"""
user FOREIGN KEY User.departments
department_name TEXT
"""
class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    users = relationship("UserDepartment", back_populates="department", lazy="selectin")
    tickets = relationship("Ticket", back_populates="department_id", lazy="selectin")

    def __repr__(self):
        return f"Department(id={self.id!r}, name={self.department_name!r})"

