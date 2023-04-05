from aiogram import Bot, F, Router, types, filters
from aiogram.fsm.context import FSMContext 

debug_router = Router()


@debug_router.message(filters.Command("get_id"))
async def group_info(message: types.Message, state: FSMContext):
    await message.answer(message.chat.id)


    

    
