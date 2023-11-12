import requests

async def calculatePP(mapId: int, *, good: int = 0, meh: int = 0, ok: int = 0, miss: int = 0, mods: list = [], combo: int | None = None, rework: str = 'live'):
    link = 'https://pp-api.huismetbenen.nl/calculate-score'

    request = {
        'map_id': mapId,
        'good': good,
        'meh': meh,
        'ok': ok,
        'miss': miss,
        'mods': mods,
        'rework': rework
    }

    if combo is not None:
        request['combo'] = combo

    return requests.patch(link, json=request).json()
