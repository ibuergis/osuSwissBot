import os

import discord
from discord.ext import commands
from discord import Option
import hashlib

from src.database.entities import Skin
from src.database.objectManager import ObjectManager
from src.helper import Validator
from src.helper.osuUserHelper import OsuUserHelper


class SkinCommands(commands.Cog):
    bot: commands.Bot

    om: ObjectManager

    validator: Validator

    osuUserHelper: OsuUserHelper

    commandGroup = discord.SlashCommandGroup("skin", "commands used to manage skins")

    def __init__(self, bot, om, validator, osuUserHelper):
        self.bot = bot
        self.om = om
        self.validator = validator
        self.osuUserHelper = osuUserHelper

    @commandGroup.command(description="get the skin from a player")
    async def get(
        self,
        ctx: discord.ApplicationContext,
        *,
        user: Option(str, description='userID or username'),  # noqa
        forcebyuserid: Option(bool,
                              description='It will skip the search via username and will find by userid: default checks for both.', # noqa
                              default=False),  # noqa

    ):
        await ctx.response.defer()
        osuUser = await self.osuUserHelper.getOsuUser(user, createIfNone=False, forceById=forcebyuserid)

        if osuUser is None or osuUser.skin is None:
            await ctx.respond('user has no skin saved')
        else:
            skin: Skin = self.om.get(Skin, osuUser.skin)
            await ctx.respond(file=discord.File(os.getcwd() + '//data//skins//' + skin.hash + '.osk', osuUser.username + '.osk'))

    @commandGroup.command(description="add a skin to a player")
    async def add(
            self,
            ctx: discord.ApplicationContext,
            *,
            user: Option(str, description='userID or username'),  # noqa
            skinfile: Option(discord.Attachment, description='add the replay file'),  # noqa
            forcebyuserid: Option(bool, description='It will skip the search via username and will find by userid: default checks for both.', default=False),  # noqa
    ):
        await ctx.response.defer()
        osuUser = await self.osuUserHelper.getOsuUser(user, createIfNone=True, forceById=forcebyuserid)
        skinfile: discord.Attachment
        data = await skinfile.read()
        hash = hashlib.sha256(data).hexdigest()

        if osuUser is None:
            await ctx.respond('username or userid ```' + user + '``` doesnt exist!')
            return None

        if osuUser.skin is not None:
            skin = self.om.get(Skin, osuUser.skin)
            if len(skin.osuUsers) <= 1:
                os.remove(os.getcwd() + '//data//skins//' + skin.hash + '.osk')
                self.om.delete(skin)

        cutSkinName = skinfile.filename.split('.')
        if 'osk' != cutSkinName[len(cutSkinName) - 1]:
            await ctx.respond('filetype should be osk')
            return None

        skin = self.om.getOneBy(Skin, Skin.hash, hash)

        if skin is None:
            with open(os.getcwd() + '//data//skins//' + hash + '.osk', 'wb+') as f:
                f.write(data)
                f.close()

            skin = Skin(hash=hash)
            self.om.add(skin)
            self.om.flush()

        osuUser.skin = skin.id
        self.om.flush()
        await ctx.respond('skin added!')

    @commandGroup.command(description="remove a skin from a player")
    async def remove(
            self,
            ctx: discord.ApplicationContext,
            *,
            user: Option(str, description='userID or username'),  # noqa
            forcebyuserid: Option(bool, description='It will skip the search via username and will find by userid: default checks for both.', default=False),  # noqa
    ):
        await ctx.response.defer()
        osuUser = await self.osuUserHelper.getOsuUser(user, createIfNone=True, forceById=forcebyuserid)

        if osuUser is None:
            await ctx.respond('username or userid ```' + user + '``` doesnt exist!')
            return None

        skin = self.om.get(Skin, osuUser.skin)
        if len(skin.osuUsers) <= 1:
            os.remove(os.getcwd() + '//data//skins//' + skin.hash + '.osk')
            self.om.delete(skin)

        osuUser.skin = None

        self.om.flush()
        await ctx.respond('Skin removed!')
