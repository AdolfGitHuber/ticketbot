from enum import Enum

class EnumDep(Enum):
    MIC = (1, "Микрофонный парк")
    MUSIC = (2, "Музыкальные Инструменты")
    AMP = (3, "Усилители")
    SPEAKER = (4, "Громкоговорители")
    RADIO = (5, "Радио оборудование")

    def __init__(self, id, title):
        self.id = id
        self.title = title

    @classmethod
    def callbacks(self):
        return {dep.name for dep in self}

    @classmethod
    def callbacks_all(self):
        cb = {dep.name for dep in self}
        cb.add('all_departments_tickets')
        return cb

    @classmethod
    def all(self):
        return [dep.id for dep in self]
