from firebase_admin import db
from typing import TypedDict

class Guild(TypedDict):
    guildId: int
    uploaders: list[int] = []


database = db.reference('/').child('guild')

def getFirstGuildBy(column: str, value: str) -> Guild|None:
    player = getGuildsBy(column, value)
    print(player)
    if len(player) == 0:
        return None
    return player[0]

def getGuildsBy(column: str, value: str) -> list[int: Guild]|None:
    return list(database.order_by_child(column).equal_to(value).get().values())

def getGuild(userId: int) -> Guild|None:
    return database.child(userId).get()

def setGuild(content: Guild):
    database.child(str(content['guildId'])).set(content)