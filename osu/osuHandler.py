import ossapi
from discord import Embed
from dataManager import DataManager
from database import DB
from entities import Player
from images import ThumbnailGenerator
import re as regex
from botFeatures.buttons import Thumbnail

from ossapi import OssapiAsync, GameMode, RankingType, ScoreType
from ossapi import Replay

from urllib.request import urlopen


class OsuHandler:
    __db: DB

    __osu: OssapiAsync

    __thumbnailGenerator: ThumbnailGenerator = ThumbnailGenerator()

    def __init__(self, db, config, test=False):


        self.__db = db
        self.__osu = OssapiAsync(int(config['clientId']),
                                 config['clientSecret'], 'http://localhost:3914/', ['public', 'identify'], grant="authorization")

    async def getUsersFromAPI(self, pages):
        players = []
        for page in range(pages):
            page += 1
            players.extend(await self.__osu.ranking(GameMode.OSU, RankingType.PERFORMANCE, country='ch', cursor={'page': page}).rankings)
        return players

    async def getUsersFromWebsite(self, pages, gamemode='osu'):
        players = []
        for page in range(pages):
            page += 1
            page = urlopen(f'https://osu.ppy.sh/rankings/osu/performance?country=CH&page={page}')
            html_bytes = page.read()
            html: str = ''.join(html_bytes.decode("utf-8").split('\n'))
            ''.join(html.split('\n'))
            playerHtmls = regex.findall('<tr.*?</tr>', html)[1:]
            for playerHtml in playerHtmls:
                SingleTD = regex.findall('<td.*?</td>', playerHtml)[:2]
                rank = regex.findall('>.*?<', SingleTD[0])[0]

                id = regex.findall('https://osu.ppy.sh/users/.*?/osu', SingleTD[1])[0].replace(
                    'https://osu.ppy.sh/users/', '').replace('/osu', '')
                linking = regex.findall('<a.*?</a>', SingleTD[1])[1]
                username = regex.findall('>.*?<', linking)[0]

                player = {
                    'rank': int(rank.replace('>', '').replace('<', '').strip().replace('#', '')),
                    'id': id,
                    'username': username.replace('>', '').replace('<', '').strip()
                }

                players.append(player)

        return players

    async def getRecentPlays(self, bot, mode: str = 'osu'):
        players = self.__db.getObjects('player')
        jsonScores = DataManager.getJson('lastScores')
        for player in players:
            scores = await self.__osu.user_scores(player.userId, ScoreType.RECENT, include_fails=False, limit=20, mode=mode)
            tempScores = []
            for score in scores:
                score: ossapi.Score
                tempScores.append(score.id)

                if str(player.userId) not in jsonScores.keys():
                    jsonScores[str(player.userId)] = []

                if score.replay is True and score.id is not None and score.id not in jsonScores[str(player.userId)]:
                    beatmap = await self.__osu.beatmap(score.beatmap.id)
                    topPlays = await self.__osu.user_scores(player.userId, ScoreType.BEST, include_fails=False, limit=20, mode=mode)
                    beatmapset = score.beatmapset
                    mods = score.mods.short_name()
                    if mods == '':
                        mods = 'NM'
                    scoreData = {
                        'id': score.id,
                        'link': f'https://osu.ppy.sh/scores/osu/{score.best_id}',
                        'statistics': {
                            'rank': score.rank.name,
                            'score': score.score,
                            'pp': score.pp,
                            'mod': mods,
                            'combo': score.max_combo,
                            'acc': str(int(score.accuracy * 10000) / 100),
                            '300': score.statistics.count_300 or 0,
                            '100': score.statistics.count_100 or 0,
                            '50': score.statistics.count_50 or 0,
                            'miss': score.statistics.count_miss or 0,
                        },
                    }
                    embed = Embed(colour=16007990)
                    embed.set_author(name=f'Score done by {player.username}', url=scoreData['link'])
                    embed.title = f'{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]'
                    embed.url = f'https://osu.ppy.sh/beatmapsets/{beatmap.beatmapset_id}#osu/{beatmap.id}'
                    embed.set_image(url=f'https://assets.ppy.sh/beatmaps/{beatmap.beatmapset_id}/covers/cover.jpg?1650602952')

                    embed.set_thumbnail(url=f'https://a.ppy.sh/{player.userId}?1692642160')
                    embed.add_field(name='Score:', value=f"{scoreData['statistics']['score']:,}")
                    embed.add_field(name='Accuracy:', value=f"{scoreData['statistics']['acc']}%")
                    embed.add_field(name='Hits:',
                                    value=f"{scoreData['statistics']['300']}/{scoreData['statistics']['100']}/{scoreData['statistics']['50']}/{scoreData['statistics']['miss']}")
                    embed.add_field(name='Combo:', value=f"{scoreData['statistics']['combo']}x")
                    embed.add_field(name='Mods:', value=mods)
                    embed.add_field(name='PP:', value=scoreData['statistics']['pp'])
                    message = ''
                    if score.pp is not None:
                        if score.pp == topPlays[0].pp:
                            message = '@everyone this is a new top play'
                        elif score.pp == topPlays[0].pp and int(score.pp//100) == int(topPlays[1].pp):
                            message = f'@everyone this person broke the {int(score.pp/100)*100}pp barrier'
                        await bot.mainChannel.send(message, embed=embed,
                                                   view=Thumbnail(self.__osu, bot, player.userId, score, beatmap))

            jsonScores[str(player.userId)] = tempScores

        DataManager.setJson('lastScores', jsonScores)

    async def updateUsers(self):
        players = self.__db.getObjects('player')
        if players != []:
            self.__db.deleteObjects(players)

        players = await self.getUsersFromWebsite(2)

        playerList = []
        for player in players:
            playerList.append(Player([None, player['id'], player['username'], player['rank']]))

        self.__db.addObjects(playerList)

        self.__db.commit()

    async def prepareReplay(self, scoreId: int, description: str = '', shortenTitle: bool = False) -> bool:
        thumbnailGenerator = ThumbnailGenerator()
        score: ossapi.Score = await self.__osu.score(ossapi.GameMode.OSU, scoreId)
        player = await self.__osu.user(score.user_id, mode=score.mode)
        beatmap = await self.__osu.beatmap(score.beatmap.id)
        await thumbnailGenerator.createThumbnail(self.__osu, player, score, beatmap, description, shortenTitle)
        try:
            replay = await self.__osu.download_score(ossapi.GameMode.OSU, score.best_id, raw=True)
            with open(f'images/output/{scoreId}.osr', 'wb+') as f:
                f.write(replay)
                f.close()
            replay = True
        except ValueError:
            replay = False

        return replay

    async def convertReplayFile(self, file: str):
        Replay(file, self.__osu)
