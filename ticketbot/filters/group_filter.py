from aiogram.filters import BaseFilter
from aiogram.types import Message

class TicketCreateFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        #check if message starts with keyword
        if message.text and message.text.lower().startswith('заявка '):
            #remove keyword from text
            text = message.text.split(' ', 1)[1]
            #check if message after keyword contains anything
            if len(text) > 0:
                return {'ticket': str(text)}
        #return false if all checks failed
        return False