from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ticketbot.models.enum.department import EnumDep
from ticketbot.models.user import User


def department_keyboard(all: bool = False) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for dep in EnumDep:
        builder.row(
            types.InlineKeyboardButton(
                text=dep.title, callback_data=dep.name
                )
            )
    if all:
        builder.row(
            types.InlineKeyboardButton(text='Все отделы', callback_data='all_departments_tickets')
        )
    return builder.as_markup()

def user_department_keyboard(departments: list) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for dep in departments:
        builder.row(
            types.InlineKeyboardButton(
                text=EnumDep[dep].title, callback_data=dep
            )
        )
    return builder.as_markup()

def user_menu_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text='Заявки', callback_data='dep_user_open_tickets'
        )
    )
    return builder.as_markup()

def admin_menu_keyboard_main() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text='Заявки', callback_data='admin_dep_tickets'
        ),
        types.InlineKeyboardButton(
            text='Управление', callback_data='admin_management'
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def admin_menu_keyboard_tickets_state() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text='Не выполнено', callback_data='admin_open_tickets'),
        types.InlineKeyboardButton(text='Выполнено', callback_data='admin_closed_tickets')
    )
    builder.adjust(1)
    return builder.as_markup()

def admin_menu_keyboard_tickets() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for dep in EnumDep:
        builder.row(
            types.InlineKeyboardButton(
                text=dep.title, callback_data=f"admin_{dep.name}"
                )
            )
    return builder.as_markup()

def admin_menu_keyboard_management() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text='Назначить пользователя в отдел', callback_data='admin_add_user_dep'
        ),
        types.InlineKeyboardButton(
            text='Удалить пользователя из отдела', callback_data='admin_remove_user_dep'
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def admin_menu_users_keyboard(users: list[User]) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.add(types.InlineKeyboardButton(
                text=user.username if user.username else user.first_name,
                callback_data=f"mgmt_{user.telegram_id}"
            )
        )
    builder.adjust(2)
    return builder.as_markup()


