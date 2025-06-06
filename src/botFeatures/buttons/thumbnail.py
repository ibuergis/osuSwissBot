import discord
import ossapi
from discord.ext import commands
from src.prepareReplay.prepareReplayManager import createAll, cleanup


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
        hasReplay: bool = createAll(
            self.osu,
            self.osu.user(self.userId, mode=self.score.beatmap.mode),
            self.score,
            self.beatmap
        )

        thumbnail: discord.File = discord.File(f'data/output/{self.score.id}.jpg')

        if hasReplay:
            replay = discord.File(f'data/output/{self.score.id}.osr')
            files = [thumbnail, replay]
        else:
            error = "**Score has no replay on the website**\n\n"
            files = [thumbnail]

        description: str = open(f'data/output/{self.score.id}Description', 'r').read()
        title: str = open(f'data/output/{self.score.id}Title', 'r').read().replace('#star#', '⭐')

        await interaction.message.reply(f'{error}title:\n```{title}```\ndescription:\n```{description}```', files=files)
        await cleanup(self.score.id)
