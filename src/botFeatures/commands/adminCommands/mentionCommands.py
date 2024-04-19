import discord
from discord.ext import commands
from discord import Option
import ossapi

from src.database.entities.discordUser import DiscordUser
from src.database.entities.guild import Guild
from src.database.objectManager import ObjectManager
from src.helper import Validator, GuildHelper


class MentionCommands(commands.Cog):
    bot: commands.Bot

    om: ObjectManager

    validator: Validator

    guildHelper: GuildHelper

    def __init__(self, bot, om, validator, guildHelper):
        self.bot = bot
        self.om = om
        self.validator = validator
        self.guildHelper = guildHelper

    def memberListEmbed(
            self,
            guild: discord.Guild,
            gamemode: ossapi.GameMode,
            mentionList: list[DiscordUser]
    ) -> discord.Embed:
        embed: discord.Embed = discord.Embed(colour=16007990)
        embed.set_author(
            name=f'Mention list for {gamemode.name.lower()}',
        )

        if not mentionList:
            embed.add_field(name='', value='List is empty')

        for user in mentionList:
            user = guild.get_member(int(user.userId))
            embed.add_field(name=user.name, value="User: " + user.mention)
        return embed

    @commands.slash_command(description="add a person to the mention list")
    async def addmention(
            self,
            ctx: discord.ApplicationContext,
            *,
            userid: Option(str, description='which user it should be'),  # noqa
            gamemode: Option(str, choices=['osu', 'mania', 'taiko', 'catch'], description='which gamemode should it be', default='osu'),  # noqa
    ):
        guild = self.om.getOneBy(Guild, Guild.guildId, str(ctx.guild_id), throw=False)
        if guild is None:
            guild = Guild(guildId=str(ctx.guild_id))
            self.om.add(guild)

        member = ctx.guild.get_member(int(userid))

        if member is None:
            await ctx.response.send_message('user does not exist')
            return None

        discordUser = self.om.getOneBy(DiscordUser, DiscordUser.userId, userid, throw=False)
        if discordUser is None:
            discordUser = DiscordUser(userId=userid)
            self.om.add(discordUser)

        try:
            gamemode: ossapi.GameMode = ossapi.GameMode.__getattribute__(ossapi.GameMode, gamemode.upper())
            if type(gamemode) is not ossapi.GameMode:
                raise KeyError
        except KeyError:
            raise ValueError("Invalid gamemode")

        self.guildHelper.addMentionForScores(guild, discordUser, gamemode)

        await ctx.response.send_message('user ' + member.mention + ' added to the ' + gamemode.name.lower() + ' scores mention list.')
        self.om.flush()

    @commands.slash_command(description="remove a user from the mention list")
    async def removemention(
            self,
            ctx: discord.ApplicationContext,
            *,
            userid: Option(str, description='which user should be removed'),  # noqa
            gamemode: Option(str, choices=['osu', 'mania', 'taiko', 'catch'], description='which gamemode should it be', default='osu'),  # noqa
    ):
        guild = self.om.getOneBy(Guild, Guild.guildId, str(ctx.guild_id), throw=False)
        if guild is None:
            guild = Guild(guildId=str(ctx.guild_id))
            self.om.add(guild)

        member = ctx.guild.get_member(int(userid))

        if member is None:
            await ctx.response.send_message('user does not exist')
            return None

        discordUser = self.om.getOneBy(DiscordUser, DiscordUser.userId, userid, throw=False)
        if discordUser is None:
            await ctx.response.send_message('user was never added to the list')

        try:
            gamemode: ossapi.GameMode = ossapi.GameMode.__getattribute__(ossapi.GameMode, gamemode.upper())
            if type(gamemode) is not ossapi.GameMode:
                raise KeyError
        except KeyError:
            raise ValueError("Invalid gamemode")

        self.guildHelper.removeMentionForScores(guild, discordUser, gamemode)

        await ctx.response.send_message('user ' + member.mention + ' removed from the ' + gamemode.name.lower() + ' scores mention list.') # noqa
        self.om.flush()

    @commands.slash_command(description="show the mention list")
    async def listmention(
            self,
            ctx: discord.ApplicationContext,
            *,
            gamemode: Option(str, choices=['osu', 'mania', 'taiko', 'catch'], description='which gamemode should it be', default='osu'),  # noqa
    ):

        guild = self.om.getOneBy(Guild, Guild.guildId, str(ctx.guild_id), throw=False)
        if guild is None:
            guild = Guild(guildId=str(ctx.guild_id))
            self.om.add(guild)

        try:
            gamemode: ossapi.GameMode = ossapi.GameMode.__getattribute__(ossapi.GameMode, gamemode.upper())
            if type(gamemode) is not ossapi.GameMode:
                raise KeyError
        except KeyError:
            raise ValueError("Invalid gamemode")

        mentionList = self.guildHelper.getMentionForScores(guild, gamemode)

        embed = self.memberListEmbed(ctx.guild, gamemode, mentionList)

        await ctx.response.send_message(embed=embed)
