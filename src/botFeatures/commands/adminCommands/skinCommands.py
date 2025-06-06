import discord
from discord.ext import commands
from discord import option

from src.helper import Validator
from src.helper.osuUserHelper import OsuUserHelper
from src.database import setPlayer
from src.helper.playerHelper import playerHasSkin

class SkinCommands(commands.Cog):
    bot: commands.Bot

    validator: Validator

    osuUserHelper: OsuUserHelper

    commandGroup = discord.SlashCommandGroup("skin", "commands used to manage skins")

    def __init__(self, bot, validator, osuUserHelper):
        self.bot = bot
        self.validator = validator
        self.osuUserHelper = osuUserHelper

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
        self.bot.loop.create_task(ctx.response.defer())
        player = self.osuUserHelper.getOsuUser(user, createIfNone=False, forceById=forcebyuserid)

        if player is None or not playerHasSkin(player):
            await ctx.respond('user has no skin saved')
        else:
            await ctx.respond(f"skin: {player['skin']}")

    @commandGroup.command(description="add a skin to a player")
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
        self.bot.loop.create_task(ctx.response.defer())
        player = self.osuUserHelper.getOsuUser(user, createIfNone=True, forceById=forcebyuserid)
        if player is None:
            await ctx.respond('username or userid ``' + user + '`` doesnt exist!')
            return None
        player['skin'] = skinlink
        setPlayer(player)
        await ctx.respond('skin added!')

    @commandGroup.command(description="remove a skin from a player")
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
        self.bot.loop.create_task(ctx.response.defer())
        player = self.osuUserHelper.getOsuUser(user, createIfNone=True, forceById=forcebyuserid)

        if player is None:
            await ctx.respond('username or userid ```' + user + '``` doesnt exist!')
            return None

        player['skin'] = None
        setPlayer(player)
        await ctx.respond('Skin removed!')
