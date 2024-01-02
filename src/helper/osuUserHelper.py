from ..database import ObjectManager
from . import Validator
from src.osuFeatures.osuHandler import OsuHandler
from ..database.entities import OsuUser


class OsuUserHelper:

    osuHandler: OsuHandler

    om: ObjectManager

    validator: Validator

    def __init__(self, osuHandler: OsuHandler, om: ObjectManager, validator: Validator):
        self.osuHandler = osuHandler
        self.om = om
        self.validator = validator

    async def getOsuUser(self, usernameOrID: str | int, *, createIfNone: bool = False, forceById: bool = False) -> OsuUser | None:
        osuUser = None
        if not forceById:
            osuUser = self.om.getOneBy(OsuUser, OsuUser.username, usernameOrID)

        if osuUser is not None:
            return osuUser

        try:
            osuUser = self.om.get(ObjectManager, int(usernameOrID))
        except ValueError:
            pass

        if osuUser is None and createIfNone:
            user = await self.osuHandler.getUserFromAPI(usernameOrID, forceById=forceById)
            if user is None:
                return None

            osuUser = OsuUser(id=user.id, username=user.username, country=user.country.code)
            self.om.add(osuUser)
            self.om.flush()

            return osuUser

        return osuUser
