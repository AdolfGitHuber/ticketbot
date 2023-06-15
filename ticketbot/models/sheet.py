from sqlalchemy import (
    Column, 
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Identity,
    func
)
from ticketbot.models.base import Base


class Sheet:
    __tablename__ = 'sheet'

    id = Column(Integer, primary_key=True)
    cell = Column(String)
    color = Column(String)
    value = Column(String)
    date = Column(DateTime(timezone=True), default=func.now())
    worker = Column(Integer, ForeignKey("user.id"))

    def __repr__(self):
        return (f"Sheet(id={self.id!r}, "
                f"cell={self.cell!r}, "
                f"color={self.color!r}, "
                f"value={self.value!r}, "
                f"date={self.date!r}, "
                f"worker={self.worker!r}")