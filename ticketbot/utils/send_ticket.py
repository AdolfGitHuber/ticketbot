import logging
from contextlib import suppress

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramForbiddenError

from sqlalchemy.ext.asyncio import AsyncSession

from ticketbot.models.enum.department import EnumDep
from ticketbot.models.enum.ticket_state import TicketState
from ticketbot.services.user_repo import UserRepository

async def send_ticket(
    session: AsyncSession,
    bot: Bot,
    ticket_text: str,
    ticket_number: int,
    state: TicketState,
    department: EnumDep
    ) -> None:
    
    dep_users = await UserRepository(session).get_department_users(department.id)

    if state == TicketState.OPEN:
        text = [
            f"Новая заявка: <code>#{ticket_number}</code>\n",
        ]
    if state == TicketState.CLOSED:
        text = [
            f"Заявка <code>#{ticket_number}</code> выполнена!\n",
        ]

    text.extend(f"<b>{ticket_text}</b>\n")


    for user in dep_users:
        with suppress(TelegramForbiddenError):
            await bot.send_message(
                chat_id=user.user_id,
                text=''.join(text),
                parse_mode='HTML'
            )