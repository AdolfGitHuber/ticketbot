from sqlalchemy import (
    Column,
    ForeignKey
)
from sqlalchemy.orm import relationship

from ticketbot.models.base import Base


class UserDepartment(Base):
    __tablename__ = 'user_department'

    user_id = Column(ForeignKey("user.telegram_id"), primary_key=True)
    department_id = Column(ForeignKey("department.id"), primary_key=True)

    user = relationship("User", back_populates="departments", lazy="selectin")
    department = relationship("Department", back_populates="users", lazy="selectin")