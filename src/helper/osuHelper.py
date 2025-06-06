from ossapi.models import NonLegacyMod, Mod

def handleModToString(mods: str | Mod | list[NonLegacyMod]):
    print(mods)
    if (not isinstance(mods, str)):
        if isinstance(mods, Mod):
            mods = legacyModToString(mods)
        elif (all(map((lambda mod: isinstance(mod,NonLegacyMod)), mods))):
            mods = nonLegacyModToString(mods)
    
    return mods

def nonLegacyModToString(mods: list[NonLegacyMod]):
    endResult = ''.join(map(lambda mod: mod.acronym if mod.acronym != 'CL' else '', mods))
    if endResult == 'NM':
        endResult = ''

    return endResult

def legacyModToString(mods: Mod):
    mod = mods.short_name()
    if mod == 'NM':
        mod = ''
    return mod
    
def modStringToList(mods: str) -> list[str]:
    n = 2
    return [mods[i:i + n] for i in range(0, len(mods), n)]