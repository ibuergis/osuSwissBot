import json

import discord
from discord.ext import commands
from database.firebase import init
from botFeatures.commands.adminCommands.skinCommands import SkinCommands
from botFeatures.commands.miscCommands import MiscCommands
from botFeatures.commands.replayCommands import ReplayCommands
from botFeatures.commands.suggestionCommands import SuggestionCommands
from helper.osuUserHelper import OsuUserHelper
from osuFeatures.osuHandler import OsuHandler
from botFeatures.commands.funCommands import FunCommands
from botFeatures.emojis import Emojis
from helper import Validator

def main():
    with open('config/config.json', 'r') as f:
        config: dict = json.load(f)
        f.close()

    intents = discord.Intents.all()
    bot = commands.Bot(intents=intents, command_prefix='$')

    #definedGuild = bot.get_guild(int(config['suggestionGuild']))
#
    #if definedGuild is None:
    #    raise ValueError("guild does not exist")
    #
    #suggestionChannel = definedGuild.get_channel(int(config['suggestionChannel']))
#
    #if suggestionChannel is None:
    #    raise ValueError("channel for suggestions does not exist")

    validator = Validator()

    osuHandler: OsuHandler = OsuHandler(config, validator)

    osuUserHelper = OsuUserHelper(osuHandler, validator)

    emojis = Emojis(bot)
    funCommands = FunCommands(bot, emojis)

    bot.add_cog(ReplayCommands(bot, osuHandler))
    bot.add_cog(SuggestionCommands(bot, osuHandler, int(config['suggestionChannel'])))
    bot.add_cog(MiscCommands(bot))
    bot.add_cog(SkinCommands(bot, osuUserHelper, int(config['uploaderRole'])))

    init()

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord!')

    @bot.event
    async def on_message(ctx: discord.Message):
        bot.loop.create_task(funCommands.checkForEasterEgg(ctx, ctx.content))

    bot.run(config['botToken'])
