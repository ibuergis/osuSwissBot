import ossapi
import requests
import re
from urllib.request import urlretrieve

class OsuDirect:
    __api: str = 'https://api.osu.direct'

    async def getBeatmapFileRaw(self, beatmap: ossapi.Beatmap):
        a = f'{self.__api}/osu/{beatmap.id}'
        file = requests.get(a, f'data/beatmaps/{beatmap.id}.osu')
        return file

    async def getBeatmapFile(self, beatmap):
        file = await self.getBeatmapFileRaw(beatmap)
        with open(f'data/beatmaps/{beatmap.id}.osu', 'w+') as f:
            f.write(file)
            f.close()

        return f'data/beatmaps/{beatmap.id}.osu'
