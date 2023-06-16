import logging
from typing import Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from ticketbot.models.enum import UserRole

logger = logging.getLogger(__name__)

class UserMessageTicketFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.text:
            if (message.text.lower().startswith('выполнено ') or
                message.text.lower().startswith('готово ')):
                #whitespace at the end excludes any punctuation
                text = message.text.split(' ', 1)[1]
                if len(text) > 0:
                    try:
                        return {'ticket_id': int(text)}
                    except ValueError:
                        return False
                return False


class AdminFilter(BaseFilter):
    async def __call__(
        self,
        message: Message,
        role: UserRole
    ) -> bool:
        if role in [UserRole.ADMIN, UserRole.OWNER]:
            return True
        return False
