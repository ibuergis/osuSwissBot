from discord.ext import tasks, commands
from src.osuFeatures.osuHandler import OsuHandler


class Automation(commands.Cog):
    __bot: commands.Bot

    __osuHandler: OsuHandler

    def __init__(self, bot: commands.Bot, osuHandler: OsuHandler, checkPlays: bool = True):
        self.__bot = bot
        self.__osuHandler = osuHandler

        if checkPlays:
            print('Recent scores are getting checked')
            self.updateUsers.start()
            self.getScores.start()
        else:
            print('Recent scores are not getting checked')

    @tasks.loop(hours=23)
    async def updateUsers(self):
        await self.__osuHandler.updateUsers()
        print('users are updated')

    @tasks.loop(minutes=20)
    async def getScores(self):
        await self.__osuHandler.getRecentPlays(self.__bot)
        print('finished updating plays')
