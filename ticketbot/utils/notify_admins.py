from aiogram import F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ticketbot.services.user_repo import UserRepo


async def register_user(message: Message, state: FSMContext):
    data = await state.get_data()
    bot = Bot.get_current()
    
    text = [
        "Новый пользователь:",
        "Никнейм: {username}".format(username=message.from_user.username),
        "Имя: {name}".format(name=message.from_user.first_name),
        "",
    ]
    





    async with data['session'] as session:
        repo = UserRepo(session)
        admins = repo.get_admins()
        for admin in admins:
            bot.send_message(admin.telegram_id, )