from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Update


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session):
        super().__init__()
        self.session = session

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session() as session:
            data["session"] = session
            return await handler(event, data)