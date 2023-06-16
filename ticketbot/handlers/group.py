import logging
from contextlib import suppress

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError

from sqlalchemy.ext.asyncio import AsyncSession

from ticketbot.filters.group_filter import TicketCreateFilter
from ticketbot.models.enum import EnumDep, TicketState
from ticketbot.services import TicketRepository, UserRepository
from ticketbot.states.ticket import TicketFSM
from ticketbot.utils import Keyboards, send_ticket

group_router = Router()
logger = logging.getLogger(__name__)

@group_router.message(TicketCreateFilter())
async def acquire_ticket(
    message: Message,
    state: FSMContext,
    ticket: str
    ) -> None:

    await state.update_data(ticket=ticket)
    await state.set_state(TicketFSM.select_department)
    
    await message.answer(
        text="Выберите отдел",
        reply_markup=Keyboards().department_keyboard()
    )


@group_router.callback_query(
    TicketFSM.select_department,
    F.data.in_(EnumDep.callbacks())
)
async def create_ticket(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot
    ) -> None:
    
    data = await state.get_data()
    await state.clear()

    async with session:
        ticket_id = await TicketRepository(session).register_new_ticket(
            text=data['ticket'],
            author=query.from_user.id,
            department=EnumDep[query.data].id
    )    
    await session.close()
    
    await send_ticket(
        session=session,
        bot=bot,
        ticket_text=data['ticket'],
        ticket_number=ticket_id,
        state=TicketState.OPEN,
        department=EnumDep[query.data]
    )
    
    user = query.from_user.username if query.from_user.username else query.from_user.first_name
    text = [
        f"Заявка <code>#{ticket_id}</code> создана!\n",
        f'Автор заявки: <a href="tg://user?id={query.from_user.id}">{user}</a>\n',
        f"Отдел: <code>{EnumDep[query.data].title}\n</code>"
        "",
    ]

    ReplyKeyboardRemove()
    await query.message.edit_text(
        text=''.join(text),
        parse_mode='HTML'
    )

