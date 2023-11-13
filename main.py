import json

import discord
from discord.ext import commands

from src.osuFeatures.osuHandler import OsuHandler
from src.botFeatures.commands.automation import Automation
from src.database.db import DB
from src.prepareReplay.prepareReplayManager import cleanup

if __name__ == '__main__':
    with open('config/config.json', 'r') as f:
        config: dict = json.load(f)
        f.close()

    test = False

    intents = discord.Intents.all()
    bot = commands.Bot(intents=intents, command_prefix='$')

    db = DB(config)

    osuHandler: OsuHandler = OsuHandler(db, config, test)

    @bot.event
    async def on_ready():
        bot.mainChannel = bot.get_channel(int(config['scoresChannel']))
        bot.add_cog(Automation(bot=bot, osuHandler=osuHandler))
        print(f'{bot.user.name} has connected to Discord!')


    @bot.slash_command()
    async def preparereplay(ctx, scoreid: int, description: str = '', shortentitle: bool = False):
        channel = bot.get_channel(ctx.channel_id)
        await ctx.respond('replay is being prepared')
        files = []
        if await osuHandler.prepareReplay(scoreid, description, shortentitle):
            error = ''
            files.append(discord.File(f'data/output/{scoreid}.osr'))
        else:
            error = f"**Score has no replay on the website**\n\n"

        files.append(discord.File(f'data/output/{scoreid}.jpg'))
        description = open(f'data/output/{scoreid}Description', 'r').read()
        title = open(f'data/output/{scoreid}Title', 'r').read().replace('#star#', '⭐')

        await channel.send(f'{error}title:\n```{title}```\ndescription:\n```{description}```', files=files)
        await cleanup(scoreid)



    @bot.slash_command()
    async def preparereplayfromfile(ctx, file: discord.Attachment):
        channel = bot.get_channel(ctx.channel_id)
        await ctx.respond('replay is being prepared')

        score = await osuHandler.prepareReplayFromFile(ctx, file)

        thumbnail = discord.File(f'data/output/{score.best_id}.jpg')
        description = open(f'data/output/{score.best_id}Description', 'r').read()
        title = open(f'data/output/{score.best_id}Title', 'r').read().replace('#star#', '⭐')

        await channel.send(f'title:\n```{title}```\ndescription:\n```{description}```', file=thumbnail)
        cleanup(score.best_id)


    bot.run(config['botToken'])

