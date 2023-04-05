from aiogram.fsm.state import StatesGroup, State



class AdminFSM(StatesGroup):
    admin_menu = State()
    admin_dep_tickets = State()
    admin_dep_management = State()
    
    