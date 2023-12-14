import discord
import ossapi
from discord.ext import commands
from src.prepareReplay.prepareReplayManager import createAll, cleanup


class Thumbnail(discord.ui.View):
    osu: ossapi.OssapiAsync

    bot: discord.Bot

    player: ossapi.User

    score: ossapi.Score

    beatmap: ossapi.Beatmap

    def __init__(
            self,
            osu: ossapi.OssapiAsync,
            bot: commands.Bot,
            user: ossapi.User,
            score: ossapi.Score, beatmap: ossapi.Beatmap
    ):
        super().__init__(timeout=1800)
        self.osu = osu
        self.bot = bot
        self.player = user
        self.score = score
        self.beatmap = beatmap

    @discord.ui.button(label="render Score", style=discord.ButtonStyle.primary, emoji="🖕")
    async def button_callback(self, button: discord.Button, interaction: discord.Interaction):
        error = ''
        hasReplay: bool = await createAll(
            self.osu,
            await self.osu.user(self.player, mode=self.score.mode),
            self.score,
            self.beatmap
        )

        thumbnail: discord.File = discord.File(f'data/output/{self.score.best_id}.jpg')

        if hasReplay:
            replay = discord.File(f'data/output/{self.score.best_id}.osr')
            files = [thumbnail, replay]
        else:
            error = "**Score has no replay on the website**\n\n"
            files = [thumbnail]

        description: str = open(f'data/output/{self.score.best_id}Description', 'r').read()
        title: str = open(f'data/output/{self.score.best_id}Title', 'r').read().replace('#star#', '⭐')

        await interaction.message.reply(f'{error}title:\n```{title}```\ndescription:\n```{description}```', files=files)
        cleanup(self.score.best_id)
