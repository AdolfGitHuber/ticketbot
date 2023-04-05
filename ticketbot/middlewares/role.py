import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from ticketbot.models.enum.role import UserRole
from ticketbot.services.user_repo import UserRepository

logger = logging.getLogger(__name__)


class RoleMiddleware(BaseMiddleware):
    def __init__(self, session, group_id, bot):
        super().__init__()
        self.session = session
        self.group_id = group_id
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = await self.bot.get_chat_member(self.group_id, event.from_user.id)
        
        if not user.status in UserRole.get_roles():
            logger.error(
                f"User {event.from_user.username, event.from_user.id, user.status}"
                f"tried to use bot with {event.text}, dropping"
            )
            return

        async with self.session() as session:
            db_user = await UserRepository(session).get_user_by_telegram_id(event.from_user.id)
            if not db_user:
                logger.info(
                    f"Adding user to database: "
                    f"{event.from_user.id, event.from_user.username, event.from_user.first_name}"
                )
                await UserRepository(session).add_user(
                    telegram_id=event.from_user.id,
                    username=event.from_user.username,
                    first_name=event.from_user.first_name,
                )
                await session.commit()


        logger.info(
            f"Message from user: {event.from_user.id,event.from_user.username}, "
            f"role: {UserRole(user.status)}, content: {event.text}"
        )
        data['role'] = UserRole(user.status)
        return await handler(event, data)