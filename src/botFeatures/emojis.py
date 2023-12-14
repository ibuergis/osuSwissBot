import discord


class Emojis:

    sataAndagi: discord.Emoji

    def __init__(self, bot: discord.Bot):
        self.sataAndagi = bot.get_emoji(1174622375086657536)
