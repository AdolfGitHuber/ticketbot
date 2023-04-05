from aiogram.fsm.state import StatesGroup, State



class TicketFSM(StatesGroup):
    select_department = State()
    
    