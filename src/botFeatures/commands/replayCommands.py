import discord
from discord import Option
from discord.ext import commands

from src.osuFeatures.osuHandler import OsuHandler
from src.prepareReplay.prepareReplayManager import cleanup

class ReplayCommands(commands.Cog):

    bot: commands.Bot

    osuHandler: OsuHandler

    def __init__(self, bot, osuHandler):
        self.bot = bot
        self.osuHandler = osuHandler

    @commands.slash_command(description="Render a thumbnail with the score ID")
    async def preparereplay(
            self, 
            ctx: discord.ApplicationContext,
            *,
            scoreid: Option(int, description='add the id of the score'),
            description: Option(str, description='a small text inside the thumbnail', default=''),
            shortentitle: Option(bool, description='removes the featured artists in the title', default=False),
            gamemode: Option(str, choices=['osu', 'mania', 'taiko', 'catch'], description='the gamemode to pick', default='osu'),
    ):
        channel = self.bot.get_channel(ctx.channel_id)
        await ctx.respond('replay is being prepared')
        await ctx.trigger_typing()
        files = []
        response = await self.osuHandler.prepareReplay(scoreid, description, shortentitle, gamemode)

        if response is None:
            await channel.send('**Score does not exist!**')
        else:
            if await self.osuHandler.prepareReplay(scoreid, description, shortentitle, gamemode):
                error = ''
                files.append(discord.File(f'data/output/{scoreid}.osr'))
            else:
                error = f"**Score has no replay on the website**\n\n"

            files.append(discord.File(f'data/output/{scoreid}.jpg'))
            description = open(f'data/output/{scoreid}Description', 'r').read()
            title = open(f'data/output/{scoreid}Title', 'r').read().replace('#star#', '⭐')

            await channel.send(f'{error}title:\n```{title}```\ndescription:\n```{description}```', files=files)
            cleanup(scoreid)

    @commands.slash_command(description="Render a thumbnail with a replay file")
    async def preparereplayfromfile(
            self,
            ctx: discord.ApplicationContext,
            *,
            replayfile: Option(discord.Attachment, description='add the replay file'),
            description: Option(str, description='a small text inside the thumbnail', default=''),
            shortentitle: Option(bool, description='removes the featured artists in the title', default=False),
    ):
        channel = self.bot.get_channel(ctx.channel_id)
        await ctx.respond('replay is being prepared')
        await ctx.trigger_typing()

        score = await self.osuHandler.prepareReplayFromFile(ctx, replayfile, description, shortentitle)
        files = [await replayfile.to_file(), discord.File(f'data/output/{score.best_id}.jpg')]
        description = open(f'data/output/{score.best_id}Description', 'r').read()
        title = open(f'data/output/{score.best_id}Title', 'r').read().replace('#star#', '⭐')

        await channel.send(f'title:\n```{title}```\ndescription:\n```{description}```', files=files)
        cleanup(score.best_id)