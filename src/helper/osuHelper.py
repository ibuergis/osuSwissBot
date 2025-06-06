from ossapi.models import NonLegacyMod, Mod

def handleModToString(mods: str | Mod | list[NonLegacyMod]):
    print(mods)
    if (not isinstance(mods, str)):
        if isinstance(mods, Mod):
            mods = legacyModToString(mods)
<<<<<<< HEAD
        elif (all(map(lambda mod: isinstance(mod, NonLegacyMod), mods))):
=======
        elif (all(map((lambda mod: isinstance(mod,NonLegacyMod)), mods))):
>>>>>>> 912e2452f6860869f8f621e1d167a1fbd617d4cd
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
