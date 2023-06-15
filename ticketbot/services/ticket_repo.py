from ticketbot.models.user import User
from ticketbot.models.ticket import Ticket
from ticketbot.models.department import Department
from ticketbot.models.enum.ticket_state import TicketState

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

class TicketRepository:

    def __init__(self, session: AsyncSession) -> None:
        """
        User related operations

        :param session: SQLAlchemy Async Session
        """
        self.session = session

    async def register_new_ticket(
        self,
        text: str,
        author: int,
        department: int
    ) -> Ticket:
        """
        Add new ticket entry to database

        :param text: Text of the ticket
        :param author: user telegram id
        :param department: department id(int) or name(str)
        :return: Ticket query, must be added to session and commited
        """
        ticket = await self.session.execute(
            insert(Ticket)
            .values(ticket_text=text,
                    author=author,
                    department=department)
            .returning(Ticket.ticket_id)
        )
        return ticket.scalars().first()

    async def change_ticket_state(
        self,
        ticket_id: int,
        state: str
    ) -> Ticket:
        """
        Change ticket state

        :param ticket_id: ticket id
        :param state: TicketState enum
        :return: False if ticket not found
        """
        ticket = await self.session.execute(
            select(Ticket)
            .where(Ticket.ticket_id == ticket_id)
        )
        ticket = ticket.scalars().first()
        if not ticket:
            return False
        ticket.state = state
        return ticket

    async def get_ticket_by_id(
        self,
        ticket_id: int
    ) -> Ticket:
        """
        Get ticket by id

        :param ticket_id: ticket id
        :return: Ticket model object
        """
        result = await self.session.execute(select(Ticket).where(Ticket.ticket_id == ticket_id))
        return result.scalars().first()

    async def get_all_department_tickets(
        self,
        department_id: int | list
    ) -> Ticket:
        """
        :param department_id: int or list of int
        :return: Ticket model object
        """
        if isinstance(department_id, int):
            result = await self.session.execute(
                select(Ticket)
                .where(Ticket.department == department_id)
            )
        if isinstance(department_id, list):
            result = await self.session.execute(
                select(Ticket)
                .where(Ticket.department.in_(department_id))
            ).order_by(Ticket.department)
        return result.scalars().all()


    async def get_department_tickets(
        self,
        department_id: int | list,
        closed: bool = False,
    ) -> Ticket:
        """
        :param department_id: int or list of int
        :param closed: return open tickets by default
        :return: Ticket model object sequence
        """
        if isinstance(department_id, int):
            result = await self.session.execute(
                select(Ticket)
                .where(
                    Ticket.department == department_id,
                    Ticket.state == ('closed' if closed else 'open')
                )
            )

        elif isinstance(department_id, list):
            result = await self.session.execute(
                select(Ticket)
                .where(
                    Ticket.department.in_(department_id),
                    Ticket.state == ('closed' if closed else 'open')
                )
                .order_by(Ticket.department)
            )
            
        return result.scalars().all()
