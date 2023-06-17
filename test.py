import json
import colorsys
import asyncio
import random

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import insert, update, select
from ticketbot.models import Base, Color, User
from ticketbot.models.enum import UserRole
from ticketbot.services import SheetRepository, UserRepository, TicketRepository


colors = {
    '0, 1, 0': ['Зеленый', 'Лозицкий'],
    '1, 1, 0': ['Желтый', 'Кожиков'],
    '1, 0, 1': ['Лиловый', 'Кондратьев'],
    '0.9843137, 0.7372549, 0.015686275': ['Грязно-оранжевый', 'Савченков'],
    '1.0, 0.6, 0.0': ['Оранжевый', None],
    '0.49803922, 0.3764706, 0.0': ['Оливковый', None],
    '0.6, 0.0, 1.0': ['Фиолетовый', None],
    '1, 0, 0': ['Красный', None],
    '1, 1, 1': ['Белый', None],
    '0': None
}
users = {

}

async def fill_colors(session):
    for color, data in colors.items():
        if isinstance(data, list):
            query = await session.execute(
                insert(Color).values(
                    name=data[0],
                    rgb=color
                )
            )

async def fill_users(session):
    for color, data in colors.items():
        colorq = await session.execute(
            select(Color.id).filter(Color.rgb == color)
        )
        color_id = colorq.scalar()

        if isinstance(data, list):
            if data[1]:
                query = await session.execute(
                    insert(User).values(
                        telegram_id=random.randint(100000, 999999),
                        first_name=data[1],
                        role=UserRole.MEMBER.value,
                        color_id=color_id
                    )
                )

async def create_tables(engine, session):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await fill_colors(session)
    await fill_users(session)
    await session.commit()

async def main():
    engine = create_async_engine(url='sqlite+aiosqlite:///test.db')
    db_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with db_session() as session:
        # await create_tables(engine, session)
        result = await SheetRepository(session).get_user_fcolor('0, 1, 0')
        print(result, result.telegram_id, result.first_name)
        print(result.color, result.color.name)

        
    



if __name__ == '__main__':
    asyncio.run(main())