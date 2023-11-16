import json

import discord
from discord.ext import commands

from src.osuFeatures import OsuHandler
from src.botFeatures import Automation, FunCommands, Emojis
from src.database import DB
from src.prepareReplay import cleanup

if __name__ == '__main__':
    with open('config/config.json', 'r') as f:
        config: dict = json.load(f)
        f.close()

    test = False

    intents = discord.Intents.all()
    bot = commands.Bot(intents=intents, command_prefix='$')

    db = DB(config)

    osuHandler: OsuHandler = OsuHandler(db, config, test)

    funCommands: FunCommands | None = None
    emojis = None

    @bot.event
    async def on_ready():
        global funCommands
        global emojis
        emojis = Emojis(bot)
        funCommands = FunCommands(bot, emojis)
        bot.mainChannel = bot.get_channel(int(config['scoresChannel']))
        bot.add_cog(Automation(bot=bot, osuHandler=osuHandler))
        print(f'{bot.user.name} has connected to Discord!')

    @bot.slash_command()
    async def invite(ctx: discord.ApplicationContext):
        await ctx.response.send_message(
            'discord server: https://discord.gg/qKvZvuJ6nP\n' +
            'invite link: https://discord.com/api/oauth2/authorize?client_id=1152379249928446074&permissions=1084479634496&scope=bot',
            ephemeral=True)


    @bot.slash_command()
    async def github(ctx: discord.ApplicationContext):
        await ctx.response.send_message(
            'https://github.com/ianbuergis/osuSwissBot',
            ephemeral=True)

    @bot.slash_command()
    async def preparereplay(ctx: discord.ApplicationContext, scoreid: int, description: str = '', shortentitle: bool = False):
        channel = bot.get_channel(ctx.channel_id)
        await ctx.respond('replay is being prepared')
        await ctx.trigger_typing()
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
        cleanup(scoreid)

    @bot.slash_command()
    async def preparereplayfromfile(ctx, file: discord.Attachment, description: str = '', shortentitle: bool = False):
        channel = bot.get_channel(ctx.channel_id)
        await ctx.respond('replay is being prepared')
        await ctx.trigger_typing()

        score = await osuHandler.prepareReplayFromFile(ctx, file, description, shortentitle)
        files = [await file.to_file(), discord.File(f'data/output/{score.best_id}.jpg')]
        description = open(f'data/output/{score.best_id}Description', 'r').read()
        title = open(f'data/output/{score.best_id}Title', 'r').read().replace('#star#', '⭐')

        await channel.send(f'title:\n```{title}```\ndescription:\n```{description}```', files=files)
        cleanup(score.best_id)

    @bot.event
    async def on_message(ctx: discord.Message):
        if funCommands is not None:
            await funCommands.checkForEasterEgg(ctx, ctx.content)

    bot.run(config['botToken'])
