import discord
import ossapi
from discord.ext import commands
from src.prepareReplay.prepareReplayManager import createAll


class Thumbnail(discord.ui.View):
    osu: ossapi.Ossapi

    bot: discord.Bot

    userId: int

    score: ossapi.Score

    beatmap: ossapi.Beatmap

    def __init__(
            self,
            osu: ossapi.Ossapi,
            bot: commands.Bot,
            userId: int,
            score: ossapi.Score, beatmap: ossapi.Beatmap
    ):
        super().__init__(timeout=1800)
        self.osu = osu
        self.bot = bot
        self.userId = userId
        self.score = score
        self.beatmap = beatmap

    @discord.ui.button(label="render Score", style=discord.ButtonStyle.primary, emoji="🖕")
    async def button_callback(self, button: discord.Button, interaction: discord.Interaction):
        error = ''
        replay = createAll(
            self.osu,
            self.osu.user(self.userId, mode=self.score.beatmap.mode),
            self.score,
            self.beatmap
        )

        thumbnail: discord.File = discord.File(replay.thumbnail)

        if replay.replayFileContent is not None:
            replay = discord.File(replay.replayFileContent)
            files = [thumbnail, replay]
        else:
            error = "**Score has no replay on the website**\n\n"
            files = [thumbnail]

        await interaction.message.reply(f'{error}title:\n```{replay.title}```\ndescription:\n```{replay.description}```', files=files)
