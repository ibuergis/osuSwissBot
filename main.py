import json
import os

import discord
from discord.ext import commands

from osuFeatures.osuHandler import OsuHandler
from botFeatures.commands.automation import Automation
from database.db import DB

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

        os.remove(f'data/output/{scoreid}Description')
        os.remove(f'data/output/{scoreid}Title')
        os.remove(f'data/output/{scoreid}.jpg')
        os.remove(f'data/output/{scoreid}.osr')


    @bot.slash_command()
    async def preparereplayfromfile(ctx, file: discord.Attachment):
        a = file.read()
        b = await file.to_file()
        c = file.save('/')
        await osuHandler.convertReplayFile(file.read())
        await ctx.channel.send('I hate osuFeatures')


    bot.run(config['botToken'])

