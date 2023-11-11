import discord
import ossapi

from src.prepareReplay.prepareReplayManager import createAll, cleanup


class Thumbnail(discord.ui.View):
    player: ossapi.User

    score: ossapi.Score

    beatmap: ossapi.Beatmap

    def __init__(self, osu: ossapi.OssapiAsync, bot, player, score, beatmap):
        super().__init__(timeout=216000)

        self.osu: ossapi.OssapiAsync = osu
        self.bot = bot
        self.player = player
        self.score: ossapi.Score = score
        self.beatmap = beatmap

    @discord.ui.button(label="render Score", style=discord.ButtonStyle.primary, emoji="🖕")
    async def button_callback(self, button: discord.Button, interaction: discord.Interaction):
        error = ''
        hasReplay = await createAll(self.osu, await self.osu.user(self.player, mode=self.score.mode), self.score,
                              self.beatmap)

        thumbnail = discord.File(f'data/output/{self.score.best_id}.jpg')

        if hasReplay:
            replay = discord.File(f'data/output/{self.score.best_id}.osr')
            files = [thumbnail, replay]
        else:
            error = f"**Score has no replay on the website**\n\n"
            files = [thumbnail]

        description = open(f'data/output/{self.score.best_id}Description', 'r').read()
        title = open(f'data/output/{self.score.best_id}Title', 'r').read().replace('#star#', '⭐')

        await interaction.message.reply(f'{error}title:\n```{title}```\ndescription:\n```{description}```', files=files)
        cleanup(self.score.best_id)
