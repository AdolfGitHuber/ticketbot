from enum import Enum

class TicketState(Enum):
    OPEN = (1, "Не выполнено")
    CLOSED = (2, "Выполнено")
    REJECTED = (3, "Отменено")
    IN_WORK = (4, "В работе")

    def __init__(self, id, title):
        self.id = id
        self.title = title
