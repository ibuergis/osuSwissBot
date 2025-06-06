import json

import discord
from discord.ext import commands

from botFeatures.commands.adminCommands.skinCommands import SkinCommands
from botFeatures.commands.miscCommands import MiscCommands
from botFeatures.commands.replayCommands import ReplayCommands
from helper.osuUserHelper import OsuUserHelper
from osuFeatures.osuHandler import OsuHandler
from botFeatures.automation import Automation
from botFeatures.commands.funCommands import FunCommands
from botFeatures.emojis import Emojis
from helper import Validator

def main():
    global loaded
    global funCommands
    loaded = False
    with open('config/config.json', 'r') as f:
        config: dict = json.load(f)
        f.close()

    intents = discord.Intents.all()
    bot = commands.Bot(intents=intents, command_prefix='$')

    validator = Validator()

    osuHandler: OsuHandler = OsuHandler(config, validator)

    osuUserHelper = OsuUserHelper(osuHandler, validator)

    funCommands = None

    bot.add_cog(ReplayCommands(bot, osuHandler))
    bot.add_cog(MiscCommands(bot))
    bot.add_cog(SkinCommands(bot, validator, osuUserHelper))

    @bot.event
    async def on_ready():
        global funCommands
        global emojis
        global loaded
    
        if not loaded:
            emojis = Emojis(bot)
            funCommands = FunCommands(bot, emojis)
            # automation = Automation(bot=bot, osuHandler=osuHandler, checkPlays=config['checkRecentPlays'])
            # bot.add_cog(automation)
            loaded = True
        print(f'{bot.user.name} has connected to Discord!')
    
    @bot.event
    async def on_message(ctx: discord.Message):
        if funCommands is not None:
            bot.loop.create_task(funCommands.checkForEasterEgg(ctx, ctx.content))
    
    bot.run(config['botToken'])
    