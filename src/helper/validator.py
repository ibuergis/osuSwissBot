import ossapi

class Validator:

    gamemodes: list[ossapi.GameMode] = [
        ossapi.GameMode.OSU,
        ossapi.GameMode.MANIA,
        ossapi.GameMode.TAIKO,
        ossapi.GameMode.CATCH
    ]

    def isGamemode(self, gamemode: ossapi.GameMode, *, throw: bool = False):
        isGamemode = gamemode in self.gamemodes
        if throw and not isGamemode:
            raise ValueError('Invalid gamemode: ' + gamemode)
        return isGamemode
