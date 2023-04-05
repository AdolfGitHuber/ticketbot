from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from ticketbot.models.user import User
from ticketbot.models.ticket import Ticket
from ticketbot.models.department import Department
from ticketbot.models.user_department import UserDepartment
from ticketbot.models.enum.role import UserRole
from ticketbot.models.enum.department import EnumDep



class UserRepository:

    def __init__(self, session: AsyncSession) -> None:
        """
        User related operations

        :param session: SQLAlchemy Async Session
        """
        self.session = session

    async def add_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str
        ) -> None:
        """
        Add a new user to the database
        
        :param telegram_id: <event>.from_user.id
        :param username: <event>.from_user.username
        :param first_name: <event>.from_user.first_name
        :param role: Enum of UserRole (default: UserRole.UNREGISTERED)
        :return: NoReturn
        """
        query = insert(User).values(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )
        _conflict = query.on_conflict_do_nothing(
            index_elements=['telegram_id']
        )
        user = await self.session.execute(_conflict)


    async def add_user_department(
        self,
        telegram_id: int | str,
        department: int,
        ) -> None:
        """
        Add user to a department
        
        :param telegram_id: <event>.from_user.id
        :param department: department id 
        :return: NoReturn
        """
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
        query = insert(UserDepartment).values(
            user_id=telegram_id,
            department_id=department
        )
        _conflict = query.on_conflict_do_nothing(
            index_elements=['user_id', 'department_id']
        )
        await self.session.execute(_conflict)

    async def remove_user_department(
        self,
        telegram_id: int | str,
        department: int
        ) -> None:
        """
        :param telegram_id: <event>.from_user.id
        :param department: department id
        :return: NoReturn
        """
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
        query = delete(UserDepartment).where(
            UserDepartment.user_id == telegram_id,
            UserDepartment.department_id == department
            )
        await self.session.execute(query)
        

    async def get_user_by_telegram_id(
        self,
        telegram_id: int | str
        ) -> User:
        """
        :param telegram_id: <event>.from_user.id
        :return: User model object of requested user or None
        """
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
        result = await self.session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
        )
        return result.scalars().first()


    async def get_admins(self) -> list[User]:
        """
        Get all admins

        :return: list of User model objects filtered by role UserRole.ADMIN
        """
        result = await self.session.execute(
            select(User)
            .where(User.role == UserRole.ADMIN)
        )
        return result.scalars().all()
    
    async def get_department_users(self, department_id: int) -> list[int]:
        """
        Get department users telegram ids

        :param department_id: EnumDep.id
        :return: list of telegram ids
        """
        result = await self.session.execute(
            select(UserDepartment)
            .where(UserDepartment.department_id == department_id)
        )
        return result.scalars().all()

    async def get_all_users(self) -> list[User]:
        """:return: list of User model objects"""
        result = await self.session.execute(
            select(User)
        )
        return result.scalars().all()
