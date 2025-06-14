import discord
from discord import option
from discord.ext import commands
import io

from src.osuFeatures.osuHandler import OsuHandler

class ReplayCommands(commands.Cog):

    bot: commands.Bot

    osuHandler: OsuHandler

    def __init__(self, bot, osuHandler):
        self.bot = bot
        self.osuHandler = osuHandler

    @commands.slash_command(description="Render a thumbnail with the score ID")
    @option('scoreid', int, description='add the id of the score')
    @option('description', str, description='a small text inside the thumbnail', default='')
    @option('shortentitle', bool, description='removes the featured artists in the title', default=False)
    async def preparereplayfromscoreid(
            self,
            ctx: discord.ApplicationContext,
            *,
            scoreid: int,
            description: str,
            shortentitle: bool = False,
    ):
        channel = self.bot.get_channel(ctx.channel_id)

        await ctx.respond('replay is being prepared')
        files = []
        response = self.osuHandler.prepareReplay(scoreid, description, shortentitle)

        if response is None:
            await channel.send('**Score does not exist!**')
            return None
        
        if response.replayFileContent is not None:
            error = ''
            files.append(discord.File(io.BytesIO(response.replayFileContent), f'{scoreid}.osr'))
        else:
            error = "**Score has no replay on the website**\n\n"

        files.append(discord.File(io.BytesIO(response.thumbnail), f'{scoreid}.jpg'))

        await channel.send(f'{error}title:\n```{response.title}```\ndescription:\n```{response.description}```', files=files)

    @commands.slash_command(description="Render a thumbnail with a replay file")
    @option('replayfile', discord.Attachment, description='add the replay file')
    @option('description', str, description='a small text inside the thumbnail', default='')
    @option('shortentitle', bool, description='removes the featured artists in the title', default=False)
    async def preparereplayfromfile(
            self,
            ctx: discord.ApplicationContext,
            *,
            replayfile: discord.Attachment,
            description: str = '',
            shortentitle: bool = False,
    ):
        channel = self.bot.get_channel(ctx.channel_id)
        self.bot.loop.create_task(ctx.respond('replay is being prepared'))

        renderedReplay = await self.osuHandler.prepareReplayFromFile(ctx, replayfile, description, shortentitle)
        files = [await replayfile.to_file(), discord.File(renderedReplay.thumbnail, 'replay.jpg')]

        await channel.send(f'title:\n```{renderedReplay.title}```\ndescription:\n```{renderedReplay.description}```', files=files)
