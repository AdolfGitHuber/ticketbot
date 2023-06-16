from ticketbot.models import Sheet

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

class SheetRepository:
    def __init__(self, session: AsyncSession) -> None:
        """
        Sheet related operations
        :param session: SQLAlchemy Async Session
        """
        self.session = session

    
    async def get_all(self):
        query = await self.session.execute(select(Sheet))
        return query.scalars().all()