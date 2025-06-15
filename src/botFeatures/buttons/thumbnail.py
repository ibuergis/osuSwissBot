import discord
import io

import ossapi
from discord.ext import commands
from src.prepareReplay.prepareReplayManager import createAll


class Thumbnail(discord.ui.View):
    osu: ossapi.Ossapi

    bot: discord.Bot

    score: ossapi.Score

    def __init__(
            self,
            osu: ossapi.Ossapi,
            bot: commands.Bot,
            score: ossapi.Score,
            user: ossapi.User|None = None
    ):
        super().__init__(timeout=1800)
        self.osu = osu
        self.bot = bot
        self.score = score
        self.user = user or score.user()

    @discord.ui.button(label="render Score", style=discord.ButtonStyle.primary, emoji="🖕")
    async def button_callback(self, button: discord.Button, interaction: discord.Interaction):
        error = ''
        response = createAll(
            self.osu,
            self.user,
            self.score,
            self.score.beatmap
        )

        thumbnail: discord.File = discord.File(io.BytesIO(response.thumbnail), str(self.score.id) + '.jpg')

        if response.replayFileContent is not None:
            replay = discord.File(io.BytesIO(response.replayFileContent), str(self.score.id) + '.osr')
            files = [thumbnail, replay]
        else:
            error = "**Score has no replay on the website**\n\n"
            files = [thumbnail]

        await interaction.message.reply(f'{error}title:\n```{response.title}```\ndescription:\n```{response.description}```', files=files)
