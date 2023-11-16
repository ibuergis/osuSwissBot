class Entity:

    id: int | None = None

    def __init__(self, values: list):
        self.id = values[0]

    def toList(self):
        return [
            self.id,
        ]
