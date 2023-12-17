import discord
from discord.ext import commands
from discord import Option

from src.database.entities.discordUser import DiscordUser
from src.database.entities.guild import Guild
from src.database.objectManager import ObjectManager

class MentionCommands(commands.Cog):
    bot: commands.Bot

    om: ObjectManager

    def __init__(self, bot, om):
        self.bot = bot
        self.om = om

    async def memberListEmbed(self, guild: discord.Guild, gamemode: str, mentionList: list[DiscordUser]) -> discord.Embed:
        embed: discord.Embed = discord.Embed(colour=16007990)
        embed.set_author(
            name=f'Mention list for {gamemode}',
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

        match gamemode:
            case 'osu':
                if discordUser not in guild.osuMentionOnTopPlay:
                    guild.osuMentionOnTopPlay.append(discordUser)
            case 'mania':
                if discordUser not in guild.maniaMentionOnTopPlay:
                    guild.maniaMentionOnTopPlay.append(discordUser)
            case 'taiko':
                if discordUser not in guild.taikoMentionOnTopPlay:
                    guild.taikoMentionOnTopPlay.append(discordUser)
            case 'catch':
                if discordUser not in guild.catchMentionOnTopPlay:
                    guild.catchMentionOnTopPlay.append(discordUser)

        await ctx.response.send_message('user ' + member.mention + ' added to the ' + gamemode + ' scores mention list.')
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

        match gamemode:
            case 'osu':
                if discordUser in guild.osuMentionOnTopPlay:
                    guild.osuMentionOnTopPlay.remove(discordUser)
            case 'mania':
                if discordUser in guild.maniaMentionOnTopPlay:
                    guild.maniaMentionOnTopPlay.remove(discordUser)
            case 'taiko':
                if discordUser in guild.taikoMentionOnTopPlay:
                    guild.taikoMentionOnTopPlay.remove(discordUser)
            case 'catch':
                if discordUser in guild.catchMentionOnTopPlay:
                    guild.catchMentionOnTopPlay.remove(discordUser)

        await ctx.response.send_message('user ' + member.mention + ' removed from the ' + gamemode + ' scores mention list.')
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

        match gamemode:
            case 'mania':
                mentionList = guild.maniaMentionOnTopPlay
            case 'taiko':
                mentionList = guild.taikoMentionOnTopPlay
            case 'catch':
                mentionList = guild.catchMentionOnTopPlay
            case _:
                mentionList = guild.osuMentionOnTopPlay

        embed = await self.memberListEmbed(ctx.guild, gamemode, mentionList)

        await ctx.response.send_message(embed=embed)
