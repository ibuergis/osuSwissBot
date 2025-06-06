import discord

import osrparse
from discord import Embed

import ossapi
from ossapi import Ossapi, GameMode, RankingType, Replay, Mod, Score, Beatmap

import os

from ossapi.models import UserStatistics

from .calculations import gradeCalculator, gradeConverter, calculateScoreViaApi

from src.database import Player
from src.helper import Validator
from src.prepareReplay.prepareReplayManager import createAll
from src.helper.osuHelper import handleModToString, modStringToList

def createScoreEmbed(player: Player, score: Score, beatmap: Beatmap, gamemode: ossapi.GameMode) -> Embed:
    if gamemode == ossapi.GameMode.MANIA:
        raise Exception('MANIA is not supported')
    mods = handleModToString(score.mods)
    embed = Embed(colour=16007990)
    beatmapset = beatmap.beatmapset()
    embed.set_author(
        name=f'Score done by {player['username']}',
        url=f'https://osu.ppy.sh/scores/{score.beatmap.mode.value}/{score.id}'

    )
    embed.title = f'{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]'
    embed.url = f'https://osu.ppy.sh/beatmapsets/{beatmap.beatmapset_id}#osuFeatures/{beatmap.id}'
    embed.set_image(
        url=f'https://assets.ppy.sh/beatmaps/{beatmap.beatmapset_id}/covers/cover.jpg?1650602952')

    embed.set_thumbnail(url=f'https://a.ppy.sh/{player['userId']}?1692642160')
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


class OsuHandler:

    __osu: Ossapi

    __validator: Validator

    def __init__(self, config: dict, validator: Validator):
        self.__validator = validator
        self.__osu = Ossapi(int(config['clientId']),
                            config['clientSecret'], 'http://localhost:3914/', ['public', 'identify'],
                            grant="authorization")

    def getUserFromAPI(self, usernameOrId: str | int, *, forceById: bool = False) -> ossapi.User:
        user = None
        if not forceById:
            try:
                user = self.__osu.user(usernameOrId)
            except ValueError:
                pass

        if user is not None:
            return user

        try:
            user = self.__osu.user(int(usernameOrId))
        except ValueError:
            pass

        return user

    def getUsersFromAPI(self, pages: int, gamemode: GameMode.OSU, country: str = 'ch') -> list[UserStatistics]:
        osuUsers = []
        for page in range(pages):
            page += 1
            result = self.__osu.ranking(gamemode, RankingType.PERFORMANCE, country=country, cursor={'page': page})
            osuUsers.extend(result.ranking)
        return osuUsers

    def prepareReplay(
            self,
            scoreId: int,
            description: str = '',
            shortenTitle: bool = False
    ) -> bool | None:
        try:
            score: ossapi.Score = self.__osu.score(scoreId)
            score.id = scoreId
        except ValueError:
            return None

        osuUser = self.__osu.user(score.user_id, mode=score.beatmap.mode)
        beatmap = self.__osu.beatmap(score.beatmap.id)
        replay = createAll(self.__osu, osuUser, score, beatmap, description, shortenTitle)
        return replay

    def convertReplayFile(self, file: discord.Attachment) -> Replay:
        replay = osrparse.Replay.from_file(file)
        ossapiReplay = ossapi.Replay(replay, self.__osu)

        return ossapiReplay

    async def prepareReplayFromFile(
            self,
            ctx,
            file: discord.Attachment, description:
            str = '', shortenTitle: bool = False
    ) -> ossapi.Score:

        await file.save(f'data/output/{ctx.author.id}.osr')
        file = open(f'data/output/{ctx.author.id}.osr', 'rb')
        replay = self.convertReplayFile(file)
        file.close()
        os.remove(f'data/output/{ctx.author.id}.osr')

        user = self.__osu.user(replay.username)
        beatmap: ossapi.Beatmap = self.__osu.beatmap(checksum=replay.beatmap_hash)

        mods = modStringToList(handleModToString(replay.mods))
        calculated = calculateScoreViaApi(
            beatmap.id, 
            s100=replay.count_100, 
            s50=replay.count_50,
            miss=replay.count_miss,
            mods=mods,
            combo=replay.max_combo
            )
        grade = gradeCalculator(replay.count_300, replay.count_100, replay.count_50, replay.count_miss)

        score = ossapi.Score()
        score.pp = calculated['performance_attributes']['pp']
        score.id = ctx.author.id if replay.replay_id is None else replay.replay_id
        score.max_combo = replay.max_combo
        score.accuracy = calculated['score']['accuracy'] / 100
        score.mods = replay.mods
        score.rank = gradeConverter(grade, replay.mods)
        score.ended_at = replay.timestamp
        score.beatmap = beatmap
        score.beatmap.mode = replay.mode
        createAll(self.__osu, user, score, beatmap, description, shortenTitle)

        return score
