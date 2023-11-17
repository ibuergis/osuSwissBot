import requests

async def calculateScoreViaApi(mapId: int, *, s100: int = 0, s50: int = 0, miss: int = 0, mods: list = [], combo: int | None = None, rework: str = 'live') -> dict:
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