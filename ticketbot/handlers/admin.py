import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from ticketbot.filters.user_filter import AdminFilter
from ticketbot.states.admin import AdminFSM
from ticketbot.models.enum.department import EnumDep
from ticketbot.services.user_repo import UserRepository
from ticketbot.utils import keyboards
from ticketbot.utils.get_tickets import get_tickets_io

logger = logging.getLogger(__name__)
admin_router = Router()

@admin_router.message(Command('menu'), AdminFilter())
async def admin_menu(
    message: Message,
    state: FSMContext,
    ) -> None:
    await state.set_state(AdminFSM.admin_menu)
    await message.answer(
        text="Я есть меню",
        reply_markup=keyboards.admin_menu_keyboard_main()
    )


@admin_router.callback_query(
    AdminFSM.admin_menu,
    F.data == 'admin_dep_tickets'
)
async def admin_menu_tickets(
    query: CallbackQuery,
    state: FSMContext,
    ) -> None:
    await state.set_state(AdminFSM.admin_dep_tickets)
    await query.answer()
    await query.message.edit_text(
        text="Выберите тип заявок",
        reply_markup=keyboards.admin_menu_keyboard_tickets_state()
    )


@admin_router.callback_query(
    AdminFSM.admin_dep_tickets,
    F.data.in_(['admin_open_tickets', 'admin_closed_tickets'])
)
async def admin_menu_ticket_state(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    if query.data == 'admin_open_tickets':
        await state.set_data({'state': False})
    if query.data == 'admin_closed_tickets':
        await state.set_data({'state': True})

    await query.answer()
    await query.message.edit_text(
        text="Выберите отделение",
        reply_markup=keyboards.department_keyboard(True)
    )


@admin_router.callback_query(
    AdminFSM.admin_dep_tickets,
    F.data.in_(EnumDep.callbacks_all())
)
async def admin_menu_dep_tickets(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot
    ) -> None:
    data = await state.get_data()
    await state.clear()
    await query.answer()

    departments = EnumDep.all() if query.data == 'all_departments_tickets' else EnumDep[query.data].id
    tickets = await get_tickets_io(
        session=session,
        department=departments,
        closed=data['state']
    )

    ReplyKeyboardRemove()
    await bot.send_document(
        chat_id=query.from_user.id,
        document=BufferedInputFile(tickets.read(), 'Заявки.txt'),
        caption="Что бы закрыть заявку напишите <code>выполнено номер_заявки </code>",
        parse_mode="HTML"
    )


@admin_router.callback_query(
    AdminFSM.admin_menu,
    F.data == 'admin_management'
)
async def admin_menu_management(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    ) -> None:
    await state.set_state(AdminFSM.admin_dep_management)
    await query.answer()
    
    async with session:
        users = await UserRepository(session).get_all_users()

    keyboard = keyboards.admin_menu_users_keyboard(users)
    await query.message.edit_text(
        text='Выберите испытуемого',
        reply_markup=keyboard,
    )

@admin_router.callback_query(
    AdminFSM.admin_dep_management,
    F.data.startswith('mgmt_')
)
async def admin_mgmt_dep_select(
    query: CallbackQuery,
    state: FSMContext,
) -> None:
    await query.answer()
    
    user = query.data.strip('mgmt_')
    
    await state.update_data({'mgmt_user': user})
    await query.message.edit_text(
        text='Выберите действие',
        reply_markup=keyboards.admin_menu_keyboard_management()
    )


@admin_router.callback_query(
    AdminFSM.admin_dep_management,
    F.data.in_(['admin_add_user_dep', 'admin_remove_user_dep'])
)
async def admin_menu_add_user_dep(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    ) -> None:
    await query.answer()
    data = await state.get_data()

    if query.data == 'admin_add_user_dep':
        await state.update_data({'mgmt_user_action': 'add'})
        keyboard = keyboards.department_keyboard()
    if query.data == 'admin_remove_user_dep':
        await state.update_data({'mgmt_user_action': 'remove'})
        async with session:
            user = await UserRepository(session).get_user_by_telegram_id(data['mgmt_user'])
        departments = [dep.department.name for dep in user.departments]
        keyboard = keyboards.user_department_keyboard(departments)


    await query.message.edit_text(
        text='Выберите отдел',
        reply_markup=keyboard
    )

@admin_router.callback_query(
    AdminFSM.admin_dep_management,
    F.data.in_(EnumDep.callbacks())
)
async def admin_mgmt_user_process(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext
) -> None:
    await query.answer()
    data = await state.get_data()
    
    async with session:
        if data['mgmt_user_action'] == 'add':
            await UserRepository(session).add_user_department(
                telegram_id=data['mgmt_user'],
                department=EnumDep[query.data].id
            )
        elif data['mgmt_user_action'] == 'remove':
            await UserRepository(session).remove_user_department(
                telegram_id=data['mgmt_user'],
                department=EnumDep[query.data].id
            )
        user = await UserRepository(session).get_user_by_telegram_id(data['mgmt_user'])
        await session.commit()

    ReplyKeyboardRemove()
    await query.message.edit_text(
        text=''.join(
            ["Пользователь: ",
            f"<code>{user.username if user.username else user.first_name}</code>\n",
            "Назначен в отдел: " if data['mgmt_user_action'] == 'add' else "Удалён из отдела: ",
            f"<code>{EnumDep[query.data].title}</code>",
            "",]
        ),
        parse_mode='HTML'
    ) 

    await state.clear()