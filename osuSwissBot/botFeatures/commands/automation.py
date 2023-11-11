from discord.ext import tasks, commands
from osu import OsuHandler


class Automation(commands.Cog):
    __bot: commands.Bot

    __osuHandler: OsuHandler

    def __init__(self, bot, osuHandler):
        self.__bot = bot
        self.__osuHandler = osuHandler

        self.updateUsers.start()
        self.getScores.start()

    @tasks.loop(hours=23)
    async def updateUsers(self):
        await self.__osuHandler.updateUsers()
        print('users are updated')

    @tasks.loop(minutes=20)
    async def getScores(self):
        await self.__osuHandler.getRecentPlays(self.__bot)
        print('finished updating plays')
