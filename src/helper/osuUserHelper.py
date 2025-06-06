from . import Validator
from src.osuFeatures.osuHandler import OsuHandler
from src.database import getFirstPlayerBy, getPlayer, setPlayer, Player

class OsuUserHelper:

    osuHandler: OsuHandler

    validator: Validator

    def __init__(self, osuHandler: OsuHandler, validator: Validator):
        self.osuHandler = osuHandler
        self.validator = validator

    def getOsuUser(self, usernameOrID: str | int, *, createIfNone: bool = False, forceById: bool = False) -> Player | None:
        player = None
        if not forceById:
            player: Player = getFirstPlayerBy('username', usernameOrID)

        if player is not None:
            return player

        try:
            player: Player = getPlayer(int(usernameOrID))
        except ValueError:
            pass

        if player is None and createIfNone:
            user = self.osuHandler.getUserFromAPI(usernameOrID, forceById=forceById)
            if user is None:
                return None

            player = setPlayer({
                'userId': user.id,
                'username': user.username,
                'skin': None
            })

            return player

        return player
