from ossapi.models import NonLegacyMod, Mod

def handleModToString(mods: str | Mod | list[NonLegacyMod]):
    if (not isinstance(mods, str)):
        if isinstance(mods, Mod):
            mods = legacyModToString(mods)
        elif (all(map(lambda mod: isinstance(mod, NonLegacyMod), mods))):
            mods = nonLegacyModToString(mods)

    return 'NM' if mods == '' else mods

def nonLegacyModToString(mods: list[NonLegacyMod]):
    endResult = ''.join(map(lambda mod: mod.acronym if mod.acronym != 'CL' else '', mods))

    return endResult

def legacyModToString(mods: Mod):
    mod = mods.short_name()
    return mod

def modStringToList(mods: str) -> list[str]:
    n = 2
    return [mods[i:i + n] for i in range(0, len(mods), n)]
