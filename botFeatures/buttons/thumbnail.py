import discord
import ossapi
from images import ThumbnailGenerator


class Thumbnail(discord.ui.View):
    player: ossapi.User

    score: ossapi.Score

    beatmap: ossapi.Beatmap

    def __init__(self, osu, bot, player, score, beatmap):
        super().__init__(timeout=216000)

        self.osu: ossapi.Ossapi = osu
        self.bot = bot
        self.player = player
        self.score: ossapi.Score = score
        self.beatmap = beatmap

    @discord.ui.button(label="render Score", style=discord.ButtonStyle.primary, emoji="🖕")
    async def button_callback(self, button: discord.Button, interaction: discord.Interaction):
        error = ''
        thumbnailGenerator = ThumbnailGenerator()
        await thumbnailGenerator.createThumbnail(self.osu, await self.osu.user(self.player, mode=self.score.mode), self.score, self.beatmap)
        try:
            replay = await self.osu.download_score(ossapi.GameMode.OSU, self.score.best_id, raw=True)
            with open('images/output/replay.osr', 'wb+') as f:
                f.write(replay)
                f.close()
        except ValueError:
            error = f"**Score has no replay on the website**\n\n"
        thumbnail = discord.File('images/output/thumbnail.jpg')
        replay = discord.File('images/output/replay.osr')
        description = open('images/output/description', 'r').read()
        title = open('images/output/title', 'r').read().replace('#star#', '⭐')
        files = [thumbnail, replay] if error == '' else [thumbnail]
        await interaction.message.reply(f'{error}title:\n```{title}```\ndescription:\n```{description}```', files=files)