class Entity:

    id: int | None = None

    def __init__(self, values):
        pass

    def toList(self):
        return [
            self.id,
        ]
