from io import BytesIO

from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from ticketbot.models.enum.department import EnumDep
from ticketbot.models.enum.ticket_state import TicketState
from ticketbot.services.ticket_repo import TicketRepository
from ticketbot.services.user_repo import UserRepository



async def get_tickets_io(
    session: AsyncSession,
    department: int | list,
    closed: bool = False
) -> BytesIO:
    async with session:
        if closed:
            tickets = await TicketRepository(session).get_department_tickets(department, True)
        else:
            tickets = await TicketRepository(session).get_department_tickets(department)


    text = []
    for ticket in tickets:
        text.append(
            f"Заявка #{ticket.ticket_id}\n"
            f"Статус: {TicketState(ticket.state).title}\n"
            f"Отдел: {EnumDep[ticket.department_id.name].title}\n"
            f"{ticket.ticket_text}\n"
            f"-----------\n"
        )

    tickets_doc = BytesIO()
    tickets_doc.write("".join(text).encode())
    tickets_doc.seek(0)

    return tickets_doc