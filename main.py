import discord
from discord.ext import commands
from discord.ext.commands.view import StringView

from images import ThumbnailGenerator

from dataManager import DataManager
from osu import OsuHandler
from botFeatures.commands import Automation
from database import DB

if __name__ == '__main__':
    dm = DataManager()
    config = dm.getJson('config/config.json')

    test = False

    intents = discord.Intents.all()
    bot = commands.Bot(intents=intents, command_prefix='$')

    db = DB(config)

    osuHandler: OsuHandler = OsuHandler(db, config, test)

    @bot.event
    async def on_ready():
        bot.mainChannel = bot.get_channel(config['scoresChannel'])
        bot.add_cog(Automation(bot=bot, osuHandler=osuHandler))
        print(f'{bot.user.name} has connected to Discord!')


    @bot.slash_command()
    async def preparereplay(ctx, scoreid: int, description: str = '', shortentitle: bool = False):
        channel = bot.get_channel(ctx.channel_id)
        await ctx.respond('replay is being prepared')
        files = [discord.File('images/output/thumbnail.jpg')]
        if await osuHandler.prepareReplay(scoreid, description, shortentitle):
            error = ''
            files.append(discord.File('images/output/replay.osr'))
        else:
            error = f"**Score has no replay on the website**\n\n"

        description = open('images/output/description', 'r').read()
        title = open('images/output/title', 'r').read().replace('#star#', '⭐')
        await channel.send(f'{error}title:\n```{title}```\ndescription:\n```{description}```', files=files)


    @bot.slash_command()
    async def preparereplayfromfile(ctx, file: discord.Attachment):
        a = file.read()
        b = await file.to_file()
        c = file.save('/')
        await osuHandler.convertReplayFile(file.read())
        await ctx.channel.send('I hate osu')


    bot.run(config['botToken'])

