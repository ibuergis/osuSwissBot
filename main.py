import json

import discord
from discord.ext import commands

from src.botFeatures.commands.adminCommands.guildCommands import GuildCommands
from src.botFeatures.commands.adminCommands.mentionCommands import MentionCommands
from src.botFeatures.commands.adminCommands.skinCommands import SkinCommands
from src.botFeatures.commands.miscCommands import MiscCommands
from src.botFeatures.commands.replayCommands import ReplayCommands
from src.database.entities.discordUser import DiscordUser
from src.helper.osuUserHelper import OsuUserHelper
from src.osuFeatures.osuHandler import OsuHandler
from src.botFeatures.automation import Automation
from src.botFeatures.commands.funCommands import FunCommands
from src.botFeatures.emojis import Emojis
from src.database import ObjectManager
from src.database.entities import Guild
from src.helper import Validator, GuildHelper

loaded = False

if __name__ == '__main__':
    with open('config/config.json', 'r') as f:
        config: dict = json.load(f)
        f.close()

    intents = discord.Intents.all()
    bot = commands.Bot(intents=intents, command_prefix='$')

    om = ObjectManager(config)

    validator = Validator()

    guildHelper = GuildHelper(validator)

    osuHandler: OsuHandler = OsuHandler(om, config, validator, guildHelper)

    osuUserHelper = OsuUserHelper(osuHandler, om, validator)

    funCommands: FunCommands | None = None
    emojis = None

    bot.add_cog(ReplayCommands(bot, osuHandler))
    bot.add_cog(MiscCommands(bot))
    bot.add_cog(GuildCommands(bot, om, validator))
    bot.add_cog(MentionCommands(bot, om, validator, guildHelper))
    bot.add_cog(SkinCommands(bot, om, validator, osuUserHelper))

@bot.event
async def on_ready():
    global funCommands
    global emojis
    global loaded

    if not loaded:
        emojis = Emojis(bot)
        funCommands = FunCommands(bot, emojis)
        automation = Automation(bot=bot, osuHandler=osuHandler, checkPlays=config['checkRecentPlays'])
        bot.add_cog(automation)
        loaded = True
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_guild_join(guild: discord.Guild):
    print('joined guild ' + str(guild.id))
    guild = Guild(guildId=str(guild.id))
    om.add(guild)
    om.flush()

@bot.event
async def on_guild_remove(guild: discord.Guild):
    print('left guild ' + str(guild.id))
    guild: Guild = om.getOneBy(Guild, Guild.guildId, str(guild.id), throw=False)
    if guild is not None:
        om.delete(guild)
        om.flush()

@bot.event
async def on_member_remove(member: discord.Member):
    discordUser = om.getOneBy(DiscordUser, DiscordUser.userId, str(member.id))
    guild = om.getOneBy(Guild, Guild.guildId, str(member.guild.id))
    if guild is None:
        guild = Guild(guildId=str(member.guild.id))
        om.add(guild)
    if discordUser is not None:
        guild.osuMentionOnTopPlay.remove(discordUser)
        guild.maniaMentionOnTopPlay.remove(discordUser)
        guild.taikoMentionOnTopPlay.remove(discordUser)
        guild.catchMentionOnTopPlay.remove(discordUser)

    om.flush()

@bot.event
async def on_message(ctx: discord.Message):
    if funCommands is not None:
        await funCommands.checkForEasterEgg(ctx, ctx.content)

bot.run(config['botToken'])
