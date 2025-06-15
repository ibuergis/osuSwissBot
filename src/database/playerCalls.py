from .firebase import init
from typing import TypedDict

class Player(TypedDict):
    username: str
    userId: int
    skin: str | None = None


db = init()

database = db.reference('/').child('player')

def getFirstPlayerBy(column: str, value: str) -> Player | None:
    player = getPlayersBy(column, value)
    if len(player) == 0:
        return None
    return player[0]

def getPlayersBy(column: str, value: str) -> list[int: Player] | None:
    return list(database.order_by_child(column).equal_to(value).get().values())

def getPlayer(userId: int) -> Player | None:
    return database.child(userId).get()

def setPlayer(content: Player) -> Player | None:
    database.child(str(content['userId'])).set(content)
