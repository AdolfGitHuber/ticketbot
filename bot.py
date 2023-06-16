import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from ticketbot.config import load_config
from ticketbot.handlers import admin_router, group_router, user_router
from ticketbot.filters.user_filter import AdminFilter
from ticketbot.utils import debug_router, GoogleSheetTracker
from ticketbot.middlewares import DbSessionMiddleware, RoleMiddleware
from ticketbot.models.base import Base


logger = logging.getLogger(__name__)


async def main():
    #logging config
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    logger.error("Starting bot")
    
    config = load_config("config/config.ini")
    
    #database config
    # engine = create_async_engine(
    #     f"postgresql+asyncpg://"
    #     f"{config.db.user}:"
    #     f"{config.db.password}@"
    #     f"{config.db.host}:"
    #     f"{config.db.port}/"
    #     f"{config.db.database}",
    #     echo=False, pool_size=10, max_overflow=0)

    engine = create_async_engine(url='sqlite+aiosqlite:///')
    db_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    #tg bot config
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(storage=MemoryStorage())
    
    #register middlewares
    dp.update.outer_middleware(DbSessionMiddleware(db_session))
    # dp.message.outer_middleware(RoleMiddleware(db_session, config.tg_bot.group_id, bot))
    
    
    #register routers
    group_router.message.filter(F.chat.type.in_({"group", "supergroup"}))
    dp.include_router(group_router)    

    user_router.message.filter(F.chat.type == "private")
    dp.include_router(user_router)

    admin_router.message.filter(F.chat.type == "private")
    dp.include_router(admin_router)

    # debug_router.message.filter(AdminFilter())
    # dp.include_router(debug_router)


    # start
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())