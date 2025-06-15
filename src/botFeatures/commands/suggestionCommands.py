import discord
from discord import option
from discord.ext import commands
from ..buttons.thumbnail import Thumbnail

from src.osuFeatures.osuHandler import OsuHandler, createScoreEmbed

class SuggestionCommands(commands.Cog):

    bot: commands.Bot

    osuHandler: OsuHandler

    commandGroup = discord.SlashCommandGroup("suggest", "suggest any score you want to the team.")

    channel: int

    submittedScores = []

    def __init__(self, bot: commands.bot, osuHandler, channel: str):
        self.bot = bot
        self.osuHandler = osuHandler
        self.channel = int(channel)

    @commandGroup.command(description="suggest score by score id")
    @option('scoreid', str, description='ID of the score')
    async def byid(
        self,
        ctx: discord.ApplicationContext,
        *,
        scoreid: str,
    ):
        if (scoreid in self.submittedScores):
            await ctx.respond('score has already been suggested')
            return None
        
        score = self.osuHandler.getScore(scoreid)

        if (score is None):
            await ctx.respond('score does not exist')
            return None
        
        self.submittedScores.append(scoreid)
        
        embed = createScoreEmbed(score)
        thumbnail = Thumbnail(self.osuHandler.osu, self.bot, score)
        await self.bot.get_channel(self.channel).send('suggestion made by ' + ctx.author.mention, embed=embed, view=thumbnail)
        await ctx.respond('suggestion has been submitted')

    @commandGroup.command(description="suggest score by replayfile")
    @option('replayfile', discord.Attachment, description='add the replay file')
    async def byfile(
        self,
        ctx: discord.ApplicationContext,
        *,
        replayfile: discord.Attachment,
    ):
        self.bot.loop.create_task(ctx.response.defer())

        score = await self.osuHandler.convertReplayFileToScore(replayfile)

        if score.replayHash in self.submittedScores:
            await ctx.respond('score has already been suggested')
            return None

        if (score is None):
            await ctx.respond('score does not exist')
            return None
        
        self.submittedScores.append(score.replayHash)
        
        embed = createScoreEmbed(score, score.user)
        thumbnail = Thumbnail(self.osuHandler.osu, self.bot, score, score.user)
        await self.bot.get_channel(self.channel).send('suggestion made by ' + ctx.author.mention, embed=embed, view=thumbnail, file=await replayfile.to_file())
        await ctx.respond('suggestion has been submitted')
