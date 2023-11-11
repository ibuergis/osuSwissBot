import os

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
            with open(f'images/output/{self.score.best_id}.osr', 'wb+') as f:
                f.write(replay)
                f.close()
        except ValueError:
            error = f"**Score has no replay on the website**\n\n"
        thumbnail = discord.File(f'images/output/{self.score.best_id}.jpg')
        replay = discord.File(f'images/output/{self.score.best_id}.osr')
        description = open(f'images/output/{self.score.best_id}Description', 'r').read()
        title = open(f'images/output/{self.score.best_id}Title', 'r').read().replace('#star#', '⭐')
        files = [thumbnail, replay] if error == '' else [thumbnail]
        await interaction.message.reply(f'{error}title:\n```{title}```\ndescription:\n```{description}```', files=files)
        os.remove(f'images/output/{self.score.best_id}Description')
        os.remove(f'images/output/{self.score.best_id}Title')
        os.remove(f'images/output/{self.score.best_id}.jpg')
        os.remove(f'images/output/{self.score.best_id}.osr')