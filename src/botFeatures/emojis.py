import discord


class Emojis:

    bot: discord.Bot

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def sataAndagi(self):
        return self.bot.get_emoji(1174622375086657536)
