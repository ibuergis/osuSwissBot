import discord

import osrparse
from discord import Embed

import ossapi
from ossapi import Ossapi, GameMode, RankingType, Replay, Score, Beatmap

import io

from ossapi.models import UserStatistics

from .calculations import gradeCalculator, gradeConverter, calculateScoreViaApi

from src.helper import Validator
from src.prepareReplay.prepareReplayManager import createAll, RenderedReplay
from src.helper.osuHelper import handleModToString, modStringToList

def createScoreEmbed(score: Score, user: ossapi.User|None = None) -> Embed:
    gamemode = score.beatmap.mode
    beatmap = score.beatmap
    player = user or score.user()
    mods = handleModToString(score.mods)
    embed = Embed(colour=16007990)
    beatmapset = beatmap.beatmapset()
    embed.set_author(
        name='Score done by ' + player.username + '\nGamemode: ' + gamemode.value.replace('osu', 'standard').replace('fruits', 'catch').capitalize(),
        url=f'https://osu.ppy.sh/scores/{score.id}'

    )
    embed.title = f'{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]'
    embed.url = f'https://osu.ppy.sh/beatmapsets/{beatmap.beatmapset_id}#osuFeatures/{beatmap.id}'
    embed.set_image(
        url=f'https://assets.ppy.sh/beatmaps/{beatmap.beatmapset_id}/covers/cover.jpg?1650602952')

    if (gamemode == ossapi.GameMode.MANIA):
        hits = (f"{score.statistics.perfect or 0}/"
             f"{score.statistics.great or 0}/"
             f"{score.statistics.good or 0}/"
             f"{score.statistics.ok or 0}/"
             f"{score.statistics.meh or 0}/"
             f"{score.statistics.miss or 0}")
    
    else:
        hits = (f"{score.statistics.great or 0}/"
             f"{score.statistics.ok or 0}/"
             f"{score.statistics.meh or 0}/"
             f"{score.statistics.combo_break or 0}/"
             f"{score.statistics.miss or 0}")

    embed.set_thumbnail(url='https://a.ppy.sh/' + str(player.id) + '?1692642160')
    embed.add_field(name='Score:', value=f"{score.total_score:,}")
    embed.add_field(name='Accuracy:', value=f"{str(int(score.accuracy * 10000) / 100)}%")
    embed.add_field(name='Hits:', value=hits)

    embed.add_field(name='Combo:', value=f"{score.max_combo}x")
    embed.add_field(name='Mods:', value=mods)
    embed.add_field(name='PP:', value=score.pp)
    return embed


class OsuHandler:

    osu: Ossapi

    __validator: Validator

    def __init__(self, config: dict, validator: Validator):
        self.__validator = validator
        self.osu = Ossapi(int(config['clientId']),
                            config['clientSecret'], 'http://localhost:' + config['callbackPort'] + '/', ['public', 'identify'],
                            grant="authorization")

    def getUserFromAPI(self, usernameOrId: str | int, *, forceById: bool = False) -> ossapi.User:
        user = None
        if not forceById:
            try:
                user = self.osu.user(usernameOrId)
            except ValueError:
                pass

        if user is not None:
            return user

        try:
            user = self.osu.user(int(usernameOrId))
        except ValueError:
            pass

        return user

    def getUsersFromAPI(self, pages: int, gamemode: GameMode.OSU, country: str = 'ch') -> list[UserStatistics]:
        osuUsers = []
        for page in range(pages):
            page += 1
            result = self.osu.ranking(gamemode, RankingType.PERFORMANCE, country=country, cursor={'page': page})
            osuUsers.extend(result.ranking)
        return osuUsers

    def prepareReplay(
            self,
            scoreId: int,
            description: str = '',
            shortenTitle: bool = False
    ) -> RenderedReplay | None:
        try:
            score: ossapi.Score = self.osu.score(scoreId)
            score.id = scoreId
        except ValueError:
            return None

        osuUser = self.osu.user(score.user_id, mode=score.beatmap.mode)
        beatmap = score.beatmap
        return createAll(self.osu, osuUser, score, beatmap, description, shortenTitle)

    def convertReplayFile(self, file: discord.Attachment) -> Replay:
        replay = osrparse.Replay.from_file(file)
        ossapiReplay = ossapi.Replay(replay, self.osu)

        return ossapiReplay

    async def convertReplayFileToScore(self, file: discord.Attachment) -> ossapi.Score:
        replayFile = io.BytesIO()
        await file.save(replayFile)
        replay = self.convertReplayFile(replayFile)

        replay.user

        user = self.osu.user(replay.username)
        beatmap: ossapi.Beatmap = self.osu.beatmap(checksum=replay.beatmap_hash)

        mods = modStringToList(handleModToString(replay.mods))
        calculated = calculateScoreViaApi(
            beatmap.id,
            s100=replay.count_100,
            s50=replay.count_50,
            miss=replay.count_miss,
            mods=mods,
            combo=replay.max_combo,
        )
        grade = gradeCalculator(replay.count_300, replay.count_100, replay.count_50, replay.count_miss)

        statistics = ossapi.Statistics()

        statistics.perfect = 0
        statistics.great = replay.count_300
        statistics.good = replay.count_100
        statistics.meh = replay.count_50
        statistics.miss = replay.count_miss
        statistics.combo_break = 0

        score = ossapi.Score()
        score.pp = calculated['performance_attributes']['pp']
        score.id = replay.replay_id
        score.max_combo = replay.max_combo
        score.accuracy = calculated['score']['accuracy'] / 100
        score.mods = replay.mods
        score.rank = gradeConverter(grade, replay.mods)
        score.ended_at = replay.timestamp
        score.beatmap = beatmap
        score.beatmap.mode = replay.mode
        score.user_id = user.id
        score.user = user
        score.total_score = replay.score
        score.statistics = statistics
        score.replayHash = replay.replay_hash

        return score

    async def prepareReplayFromFile(
            self,
            ctx,
            file: discord.Attachment,
            description: str = '',
            shortenTitle: bool = False
    ) -> RenderedReplay:

        replayFile = io.BytesIO()
        await file.save(replayFile)
        replay = self.convertReplayFile(replayFile)

        user = self.osu.user(replay.username)
        beatmap: ossapi.Beatmap = self.osu.beatmap(checksum=replay.beatmap_hash)

        mods = modStringToList(handleModToString(replay.mods))
        calculated = calculateScoreViaApi(
            beatmap.id,
            s100=replay.count_100,
            s50=replay.count_50,
            miss=replay.count_miss,
            mods=mods,
            combo=replay.max_combo,
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
        return createAll(self.osu, user, score, beatmap, description, shortenTitle)

    def getScore(self, scoreId: str):
        try:
            score: ossapi.Score = self.osu.score(scoreId)
            score.id = scoreId
        except ValueError:
            return None
        
        return score
