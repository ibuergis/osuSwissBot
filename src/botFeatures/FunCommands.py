import discord
from discord.ext import commands
from .emojis import Emojis


class FunCommands:

    bot: discord.Bot

    emojis: Emojis

    def __init__(self, bot: commands.Bot, emojis: Emojis):
        self.bot = bot
        self.emojis = emojis

    async def checkForEasterEgg(self, ctx: discord.Message, phrase: str):
        if 'sata andagi' in phrase:
            await ctx.add_reaction(self.emojis.sataAndagi)
