from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ticketbot.models import User
from ticketbot.models.enum import EnumDep


class Keyboards(InlineKeyboardBuilder):
    def __init__(self):
        super().__init__()


    def department_keyboard(self, all: bool = False) -> types.InlineKeyboardMarkup:
        for dep in EnumDep:
            self.row(
                types.InlineKeyboardButton(
                    text=dep.title, callback_data=dep.name
                    )
                )
        if all:
            self.row(
                types.InlineKeyboardButton(text='Все отделы', callback_data='all_departments_tickets')
            )
        return self.as_markup()


    def user_department_keyboard(self, departments: list) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for dep in departments:
            self.row(
                types.InlineKeyboardButton(
                    text=EnumDep[dep].title, callback_data=dep
                )
            )
        return self.as_markup()

    def user_menu_keyboard(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        self.add(
            types.InlineKeyboardButton(
                text='Заявки', callback_data='dep_user_open_tickets'
            )
        )
        return self.as_markup()

    def admin_menu_keyboard_main(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        self.add(
            types.InlineKeyboardButton(
                text='Заявки', callback_data='admin_dep_tickets'
            ),
            types.InlineKeyboardButton(
                text='Управление', callback_data='admin_management'
            )
        )
        self.adjust(1)
        return self.as_markup()

    def admin_menu_keyboard_tickets_state(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        self.add(
            types.InlineKeyboardButton(text='Не выполнено', callback_data='admin_open_tickets'),
            types.InlineKeyboardButton(text='Выполнено', callback_data='admin_closed_tickets')
        )
        self.adjust(1)
        return self.as_markup()

    def admin_menu_keyboard_tickets(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for dep in EnumDep:
            self.row(
                types.InlineKeyboardButton(
                    text=dep.title, callback_data=f"admin_{dep.name}"
                    )
                )
        return self.as_markup()

    def admin_menu_keyboard_management(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        self.add(
            types.InlineKeyboardButton(
                text='Назначить пользователя в отдел', callback_data='admin_add_user_dep'
            ),
            types.InlineKeyboardButton(
                text='Удалить пользователя из отдела', callback_data='admin_remove_user_dep'
            )
        )
        self.adjust(1)
        return self.as_markup()

    def admin_menu_users_keyboard(self, users: list[User]) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for user in users:
            self.add(types.InlineKeyboardButton(
                    text=user.username if user.username else user.first_name,
                    callback_data=f"mgmt_{user.telegram_id}"
                )
            )
        self.adjust(2)
        return self.as_markup()


