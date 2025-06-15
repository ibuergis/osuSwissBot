import discord
from discord.ext import commands
from discord import option

from src.helper.osuUserHelper import OsuUserHelper
from src.database import setPlayer
from src.helper.playerHelper import playerHasSkin
from src.helper.permissionHelper import memberIsUploader

class SkinCommands(commands.Cog):
    bot: commands.Bot

    osuUserHelper: OsuUserHelper

    commandGroup = discord.SlashCommandGroup("skin", "commands used to manage skins")

    adminGroup = commandGroup.create_subgroup('admin', 'admin commands for skins')

    uploaderRole: int|None = None

    def __init__(self, bot, osuUserHelper, uploaderRole):
        self.bot = bot
        self.osuUserHelper = osuUserHelper
        self.uploaderRole = uploaderRole

    @commandGroup.command(description="get the skin from a player")
    @option('user', str, description='userID or username')
    @option(
        'forcebyuserid',
        bool,
        description='It will skip the search via username and will find by userid: default checks for both.',
        default=False)
    async def get(
        self,
        ctx: discord.ApplicationContext,
        *,
        user: str,
        forcebyuserid: bool = False
    ):
        if not ctx.guild:
            return None
        player = self.osuUserHelper.getOsuUser(user, createIfNone=False, forceById=forcebyuserid)

        if player is None or not playerHasSkin(player):
            await ctx.respond('user has no skin saved')
        else:
            await ctx.respond(f"skin: {player['skin']}")


    @commandGroup.command(description="add your own skin")
    @option('skinlink', str, description='link to the skin')
    async def add(self, ctx: discord.ApplicationContext, skinlink: str,):
        if not ctx.guild:
            return None
        player = self.osuUserHelper.getOsuUser(ctx.author.nick or ctx.author.name, createIfNone=True, forceById=False)
        print(player, ctx.author.nick)
        if (player is None):
            await ctx.respond('there is no osu account that uses your nickname. please ask the mods for a namechange or give the youtube channel staff the link to add it.')
            return None
        player['skin'] = skinlink
        setPlayer(player)
        await ctx.respond('skin added!')

    @commandGroup.command(description="remove your own skin")
    async def remove(self, ctx: discord.ApplicationContext):
        if not ctx.guild:
            return None
        player = self.osuUserHelper.getOsuUser(ctx.author.nick, createIfNone=True, forceById=False)

        if player is None:
            await ctx.respond('there is no osu account that uses your nickname. please ask the mods for a namechange or tell the youtube channel staff to remove it.')
            return None

        player['skin'] = None
        setPlayer(player)
        await ctx.respond('Skin removed!')

    @adminGroup.command(description="staff command|add a skin to a player")
    @option('user', str, description='userID or username')
    @option('skinlink', str, description='link to the skin')
    @option(
        'forcebyuserid', bool,
        description='It will skip the search via username and will find by userid: default checks for both.',
        default=False
    )
    async def add(
            self,
            ctx: discord.ApplicationContext,
            *,
            user: str,
            skinlink: str,
            forcebyuserid: bool = False,
    ):
        if not ctx.guild:
            return None
        if not memberIsUploader(self.uploaderRole, ctx.author):
            await ctx.respond('No permission to use the command')
            return None
        player = self.osuUserHelper.getOsuUser(user, createIfNone=True, forceById=forcebyuserid)
        if player is None:
            await ctx.respond('username or userid ``' + user + '`` doesnt exist!')
            return None
        player['skin'] = skinlink
        setPlayer(player)
        await ctx.respond('skin added!')

    @adminGroup.command(description="staff command|remove a skin from a player")
    @option('user', str, description='userID or username')
    @option(
        'forcebyuserid',
        bool,
        description='It will skip the search via username and will find by userid: default checks for both.',
        default=False
    )
    async def remove(
            self,
            ctx: discord.ApplicationContext,
            *,
            user: str,
            forcebyuserid: bool = False,
    ):
        if not ctx.guild:
            return None
        if not memberIsUploader(self.uploaderRole, ctx.author):
            await ctx.respond('No permission to use the command')
            return None

        player = self.osuUserHelper.getOsuUser(user, createIfNone=True, forceById=forcebyuserid)

        if player is None:
            await ctx.respond('username or userid ```' + user + '``` doesnt exist!')
            return None

        player['skin'] = None
        setPlayer(player)
        await ctx.respond('Skin removed!')
