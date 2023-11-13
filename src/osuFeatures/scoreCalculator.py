import os

import ossapi
import requests
from peace_performance_python import Calculator, Beatmap
from src.osuFeatures.mirrors.osuDirect import OsuDirect


async def calculateScoreViaApi(mapId: int, *, s100: int = 0, s50: int = 0, miss: int = 0, mods: list = [], combo: int | None = None, rework: str = 'live'):
    link = 'https://pp-api.huismetbenen.nl/calculate-score'

    request = {
        'map_id': mapId,
        'good': s100,
        'ok': s100,
        'meh': s50,
        'miss': miss,
        'mods': mods,
        'rework': rework
    }

    if combo is not None:
        request['combo'] = combo

    return requests.patch(link, json=request).json()

async def calculateScoreViaRosu(beatmap: ossapi.Beatmap, *, s100: int = 0, s50: int = 0, miss: int = 0, mods: int, combo: int | None = None, mode: int = 0):
    osuDirect = OsuDirect()
    path = await osuDirect.getBeatmapFile(beatmap)
    beatmap = Beatmap(path)

    calculator = Calculator()
    calculator.set_n100(s100)
    calculator.set_n50(s50)
    calculator.set_miss(miss)
    calculator.set_mods(mods)
    calculator.set_combo(combo)
    calculator.set_mode(mode)
    answer = calculator.calculate(beatmap)
    del beatmap
    os.remove(path)

