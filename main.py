import json

import discord
from discord.ext import commands

from src.botFeatures.commands.miscCommands import MiscCommands
from src.botFeatures.commands.replayCommands import ReplayCommands
from src.osuFeatures.osuHandler import OsuHandler
from src.botFeatures.automation import Automation
from src.botFeatures.commands.funCommands import FunCommands
from src.botFeatures.emojis import Emojis
from src.database.db import DB

if __name__ == '__main__':
    with open('config/config.json', 'r') as f:
        config: dict = json.load(f)
        f.close()

    intents = discord.Intents.all()
    bot = commands.Bot(intents=intents, command_prefix='$')

    db = DB(config)

    osuHandler: OsuHandler = OsuHandler(db, config)

    funCommands: FunCommands | None = None
    emojis = None

    bot.add_cog(ReplayCommands(bot, osuHandler))
    bot.add_cog(MiscCommands(bot))

    @bot.event
    async def on_ready():
        global funCommands
        global emojis
        emojis = Emojis(bot)
        funCommands = FunCommands(bot, emojis)
        bot.mainChannel = bot.get_channel(int(config['scoresChannel']))
        bot.add_cog(Automation(bot=bot, osuHandler=osuHandler, checkPlays=config['checkRecentPlays']))
        print(f'{bot.user.name} has connected to Discord!')

    @bot.event
    async def on_message(ctx: discord.Message):
        if funCommands is not None:
            await funCommands.checkForEasterEgg(ctx, ctx.content)

    bot.run(config['botToken'])
