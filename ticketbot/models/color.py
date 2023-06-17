from sqlalchemy import (
    Column, 
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from . import Base


class Color(Base):
    __tablename__ = 'color'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    rgb = Column(String)

    user_clr = relationship("User", back_populates="color")

    def __repr__(self):
        return (f"Color(id={self.id!r}, "
                f"name={self.name!r}, "
                f"rgb={self.rgb!r})")