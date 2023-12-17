from msilib.schema import File
from typing import Any

import osrparse
from discord import Embed
from discord.ext import commands

import ossapi
from ossapi import OssapiAsync, GameMode, RankingType, ScoreType, Replay

import os
import re as regex

from .calculations import gradeCalculator, gradeConverter, calculateScoreViaApi

from ..dataManager import DataManager
from ..database.objectManager import ObjectManager
from ..database.entities.osuUser import OsuUser
from ..prepareReplay.prepareReplayManager import createAll
from ..botFeatures.buttons.thumbnail import Thumbnail

from urllib.request import urlopen


async def getUsersFromWebsite(pages: int, gameMode = GameMode.OSU, country='ch') -> list[dict[str | int, Any]]:
    osuUsers = []
    for page in range(pages):
        page += 1
        page = urlopen(f'https://osu.ppy.sh/rankings/{gameMode}/performance?country={country}&page={page}')
        html_bytes = page.read()
        html: str = ''.join(html_bytes.decode("utf-8").split('\n'))
        ''.join(html.split('\n'))
        osuUsersHtml = regex.findall('<tr.*?</tr>', html)[1:]
        for osuUserHtml in osuUsersHtml:
            SingleTD = regex.findall('<td.*?</td>', osuUserHtml)[:2]
            rank = regex.findall('>.*?<', SingleTD[0])[0]

            id = regex.findall(f'https://osu.ppy.sh/users/.*?/{gameMode}', SingleTD[1])[0].replace(
                'https://osu.ppy.sh/users/', '').replace(f'/{gameMode}', '')
            linking = regex.findall('<a.*?</a>', SingleTD[1])[1]
            username = regex.findall('>.*?<', linking)[0]

            osuUser = {
                'rank': int(rank.replace('>', '').replace('<', '').strip().replace('#', '')),
                'id': int(id),
                'username': username.replace('>', '').replace('<', '').strip()
            }

            osuUsers.append(osuUser)

    return osuUsers


async def createScoreEmbed(osuUser: OsuUser, score: ossapi.Score, beatmap: ossapi.Beatmap) -> Embed:
    mods = score.mods.short_name()
    if mods == '':
        mods = 'NM'
    embed = Embed(colour=16007990)
    beatmapset = beatmap.beatmapset()
    embed.set_author(
        name=f'Score done by {osuUser.username}',
        url=f'https://osu.ppy.sh/scores/{score.mode.value}/{score.best_id}'

    )
    embed.title = f'{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]'
    embed.url = f'https://osu.ppy.sh/beatmapsets/{beatmap.beatmapset_id}#osuFeatures/{beatmap.id}'
    embed.set_image(
        url=f'https://assets.ppy.sh/beatmaps/{beatmap.beatmapset_id}/covers/cover.jpg?1650602952')

    embed.set_thumbnail(url=f'https://a.ppy.sh/{osuUser.id}?1692642160')
    embed.add_field(name='Score:', value=f"{score.score:,}")
    embed.add_field(name='Accuracy:', value=f"{str(int(score.accuracy * 10000) / 100)}%")
    embed.add_field(name='Hits:',
                    value=f"{score.statistics.count_300 or 0}/"
                          f"{score.statistics.count_100 or 0}/"
                          f"{score.statistics.count_50 or 0}/"
                          f"{score.statistics.count_miss or 0}")

    embed.add_field(name='Combo:', value=f"{score.max_combo}x")
    embed.add_field(name='Mods:', value=mods)
    embed.add_field(name='PP:', value=score.pp)
    return embed


async def convertModsToList(mods: ossapi.Mod) -> list[str]:
    mod = mods.short_name()
    if mod == 'NM':
        mod = ''
    n = 2
    return [mod[i:i + n] for i in range(0, len(mod), n)]


class OsuHandler:
    __om: ObjectManager

    __osu: OssapiAsync

    def __init__(self, om: ObjectManager, config: dict):
        self.__om = om
        self.__osu = OssapiAsync(int(config['clientId']),
                                 config['clientSecret'], 'http://localhost:3914/', ['public', 'identify'],
                                 grant="authorization")

    async def getUsersFromAPI(self, pages: int, gamemode: GameMode.OSU) -> list[ossapi.User]:
        osuUsers = []
        for page in range(pages):
            page += 1
            osuUsers.extend(await self.__osu.ranking(gamemode, RankingType.PERFORMANCE, country='ch',
                                                     cursor={'page': page}).rankings)
        return osuUsers

    async def processRecentUserScores(self, bot: commands.Bot, osuUser: OsuUser, mode: GameMode.OSU):
        scores = await self.__osu.user_scores(osuUser.id, ScoreType.RECENT, include_fails=False, limit=20, mode=mode)
        jsonScores = DataManager.getOrCreateJson('lastScores')
        tempScores = []
        for score in scores:
            score: ossapi.Score
            tempScores.append(score.id)
            if str(osuUser.id) not in jsonScores.keys():
                jsonScores[str(osuUser.id)] = []

            if score.replay is True and score.id is not None and score.id not in jsonScores[str(osuUser.id)]:
                beatmap = await self.__osu.beatmap(score.beatmap.id)
                topPlays = await self.__osu.user_scores(osuUser.id, ScoreType.BEST, include_fails=False, limit=20,
                                                        mode=mode)

                message = ''
                if score.pp is not None:
                    if score.pp == topPlays[0].pp:
                        message = '@everyone this is a new top play'
                    elif score.pp == topPlays[0].pp and int(score.pp // 100) == int(topPlays[1].pp):
                        message = f'@everyone this person broke the {int(score.pp / 100) * 100}pp barrier'
                    await bot.mainChannel.send(message, embed=await createScoreEmbed(osuUser, score, beatmap),
                                               view=Thumbnail(self.__osu, bot, osuUser.id, score, beatmap))

        jsonScores[str(osuUser.id)] = tempScores
        DataManager.setJson('lastScores', jsonScores)

    async def getRecentPlays(self, bot: commands.Bot, mode: ossapi.GameMode = ossapi.GameMode.OSU, ranks: list[int] | None=None):
        match mode:
            case ossapi.GameMode.OSU:
                osuUserFilter = OsuUser.osuRank
            case ossapi.GameMode.MANIA:
                osuUserFilter = OsuUser.maniaRank
            case ossapi.GameMode.TAIKO:
                osuUserFilter = OsuUser.taikoRank
            case ossapi.GameMode.CATCH:
                osuUserFilter = OsuUser.catchRank
            case _:
                raise Exception('Define a valid gamemode')

        select = self.__om.select(OsuUser)
        if ranks is None:
            select = select.where(osuUserFilter is not None)
        else:
            select = select.where(osuUserFilter.in_(tuple(ranks)))

        osuUsers: list[OsuUser] = self.__om.execute(select).scalars()

        for osuUser in osuUsers:
             await self.processRecentUserScores(bot, osuUser, mode)

    async def updateUsers(self):
        osuUsers = await getUsersFromWebsite(2, GameMode.OSU, 'ch')

        for osuUserData in osuUsers:
            osuUser: OsuUser = self.__om.get(OsuUser, osuUserData['id'])

            if osuUser is None:
                osuUser = OsuUser(
                    id=osuUserData['id'],
                    username=osuUserData['username'],
                    osuRank=osuUserData['rank'],
                    country='ch'
                )
                self.__om.add(osuUser)
            else:
                osuUser.username = osuUserData['username']
                osuUser.osuRank = osuUserData['rank']

        self.__om.flush()

    async def prepareReplay(
            self,
            scoreId: int,
            description: str = '',
            shortenTitle: bool = False,
            gamemode: str = 'osu'
    ) -> bool | None:

        gamemode = gamemode.lower()
        gamemodes = {
            'osu': ossapi.GameMode.OSU,
            'mania': ossapi.GameMode.MANIA,
            'taiko': ossapi.GameMode.TAIKO,
            'catch': ossapi.GameMode.CATCH
        }
        mode = gamemodes[gamemode]
        try:
            score: ossapi.Score = await self.__osu.score(mode, scoreId)
        except ValueError:
            return None

        osuUser = await self.__osu.user(score.user_id, mode=score.mode)
        beatmap = await self.__osu.beatmap(score.beatmap.id)
        replay = await createAll(self.__osu, osuUser, score, beatmap, description, shortenTitle)
        return replay

    async def convertReplayFile(self, file: File) -> Replay:
        replay = osrparse.Replay.from_file(file)
        ossapiReplay = ossapi.Replay(replay, self.__osu)

        return ossapiReplay

    async def prepareReplayFromFile(
            self,
            ctx,
            file: File, description:
            str = '', shortenTitle: bool = False,
            gamemode: str = 'osu'
    ) -> ossapi.Score:

        await file.save(f'data/output/{ctx.author.id}.osr')
        file = open(f'data/output/{ctx.author.id}.osr', 'rb')
        replay = await self.convertReplayFile(file)
        file.close()
        os.remove(f'data/output/{ctx.author.id}.osr')

        user = await self.__osu.user(replay.username)
        beatmap: ossapi.Beatmap = await self.__osu.beatmap(checksum=replay.beatmap_hash)

        mods = await convertModsToList(replay.mods)
        calculated = await calculateScoreViaApi(beatmap.id, s100=replay.count_100, s50=replay.count_50,
                                                miss=replay.count_miss, mods=mods, combo=replay.max_combo)
        grade = await gradeCalculator(replay.count_300, replay.count_100, replay.count_50, replay.count_miss)

        score = ossapi.Score()
        score.pp = calculated['local_pp']
        score.best_id = ctx.author.id if replay.replay_id is None else replay.replay_id
        score.max_combo = replay.max_combo
        score.accuracy = calculated['accuracy'] / 100
        score.mods = replay.mods
        score.rank = await gradeConverter(grade, replay.mods)
        score.created_at = replay.timestamp
        score.mode = replay.mode
        await createAll(self.__osu, user, score, beatmap, description, shortenTitle)

        return score
