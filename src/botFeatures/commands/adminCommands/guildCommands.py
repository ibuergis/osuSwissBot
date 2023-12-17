import discord
from discord.ext import commands
from discord import Option

from src.database.entities.guild import Guild
from src.database.objectManager import ObjectManager

class GuildCommands(commands.Cog):

    bot: commands.Bot

    om: ObjectManager

    def __init__(self, bot, om):
        self.bot = bot
        self.om = om

    @commands.slash_command(description="Decide which channel the scores should be spammed on")
    @commands.has_permissions(administrator=True)
    async def setscorechannel(
            self,
            ctx: discord.ApplicationContext,
            *,
            channelid: Option(str, description='which channel it should be'),  # noqa
            gamemode: Option(str, choices=['osu', 'mania', 'taiko', 'catch'], description='which gamemode should it be',default='osu'),  # noqa
    ):

        guild = self.om.getOneBy(Guild, Guild.guildId, str(ctx.guild_id), throw=False)
        if guild is None:
            guild = Guild(guildId=str(ctx.guild_id))
            self.om.add(guild)

        channel = ctx.guild.get_channel(int(channelid))

        if (channel is None):
            await ctx.response.send_message('This channel does not exist or isnt from this guild')
            return None

        match gamemode:
            case 'osu':
                guild.osuScoresChannel = channelid
            case 'mania':
                guild.maniaScoresChannel = channelid
            case 'taiko':
                guild.taikoScoresChannel = channelid
            case 'catch':
                guild.catchScoresChannel = channelid

        await ctx.response.send_message('set Score channel for ' + gamemode + ' to ' + channel.mention)
        self.om.flush()
