from ticketbot.models import Sheet

from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ticketbot.models import Sheet, User, Color

class SheetRepository:
    def __init__(self, session: AsyncSession) -> None:
        """
        Sheet related operations
        :param session: SQLAlchemy Async Session
        """
        self.session = session

    
    async def get_sheet(self) -> Sheet:
        query = await self.session.execute(select(Sheet))
        return query.scalars().all()
    
    async def get_user_fcolor(self, color: str) -> User:
        query = select(User).join(Color)\
                .options(selectinload(User.color)).filter(Color.rgb == color)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def set_user_color(self, telegram_id: int, color: str) -> User:
        subq = select(Color.id).filter(Color.rgb == color)
        query = update(User).filter(User.telegram_id == telegram_id).values(
            color_id=subq.scalar_subquery()
        ).returning(User.id)
        result = await self.session.execute(query)
        return result.scalars().first()
        
