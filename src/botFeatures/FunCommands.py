import discord
from .emojis import Emojis

class FunCommands:

    emojis: Emojis

    def __init__(self, emojis: Emojis):
        self.emojis = emojis

    async def checkForShitpost(self, ctx: discord.Message, phrase: str):
        if 'sata andagi' in phrase:
            await ctx.add_reaction(self.emojis.sataAndagi)
