import logging
from io import BytesIO

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command, CommandObject, Text
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from ticketbot.states.user import UserStates
from ticketbot.filters.user_filter import UserMessageTicketFilter
from ticketbot.services.user_repo import UserRepository
from ticketbot.services.ticket_repo import TicketRepository
from ticketbot.models.enum.department import EnumDep
from ticketbot.models.enum.ticket_state import TicketState
from ticketbot.utils.keyboards import user_menu_keyboard
from ticketbot.utils.send_ticket import send_ticket
from ticketbot.utils.get_tickets import get_tickets_io

user_router = Router()
logger = logging.getLogger(__name__)

@user_router.message(Command('start'))
async def user_start(
    message: Message,
    state: FSMContext
    ) -> None:
    
    await state.set_state(UserStates.menu)

    await message.answer(
        text="Меню заявок",
        reply_markup=user_menu_keyboard(),
    )


@user_router.callback_query(
    UserStates.menu,
    F.data == "dep_user_open_tickets"
)
async def user_tickets(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot
    ) -> None:
    async with session:
        user = await UserRepository(session).get_user_by_telegram_id(query.from_user.id)
        
    await query.answer()
    if not user.departments:
        await query.message.answer('Вы не состоите ни в одном подразделении')
        return
        
    departments = [dep.department.id for dep in user.departments]
    tickets = await get_tickets_io(session, departments)

    await bot.send_document(
        chat_id=query.from_user.id,
        document=BufferedInputFile(tickets.read(), 'Заявки.txt'),
        caption="Что бы закрыть заявку напишите <code>выполнено номер_заявки </code>",
        parse_mode="HTML"
    )


@user_router.message(UserMessageTicketFilter())
async def ticket_cmd(
    message: Message,
    session: AsyncSession,
    bot: Bot,
    ticket_id: int = None,
    data: dict = None
    ) -> None:
    async with session:
        ticket = await TicketRepository(session).get_ticket_by_id(ticket_id)
        user = await UserRepository(session).get_user_by_telegram_id(message.from_user.id)
        departments = [EnumDep[dep.department.name].title for dep in user.departments]
        #check if any tickets found
        if ticket:
            #if user is not admin, he can only see his department tickets
            if not data['role'] in ['administrator', 'creator']:
                if ticket.department_id not in user.departments:
                    await message.answer(
                        text=f"Вы не можете закрыть заявку с номером <code>#{ticket.ticket_id}</code>\n"
                            "Отдел назначенный на заявку: "
                            f"<code>{EnumDep[ticket.department_id.name].title}</code>\n"
                            "Вы состоите в отделах: "
                            f"<code>{', '.join(departments)}</code>\n",
                            parse_mode='HTML'
                    )
                    return
            #if ticket already closed there's no need to close it again
            if ticket.state == TicketState.CLOSED:
                await message.answer(text=f"Заявка #{ticket.ticket_id} уже выполнена")
                return
            #close ticket when all checks passed
            ticket.state = TicketState.CLOSED
        await session.commit()
    
    await send_ticket(
        session=session,
        bot=bot,
        ticket_text=ticket.ticket_text,
        ticket_number=ticket.ticket_id,
        state=TicketState.CLOSED,
        department=ticket.department_id
    )


        

    
        