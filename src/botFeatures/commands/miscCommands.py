import discord
from discord.ext import commands

class MiscCommands(commands.Cog):

    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def invite(self, ctx: discord.ApplicationContext):
        await ctx.response.send_message(
            'discord server: https://discord.gg/qKvZvuJ6nP'
            'invite link: '
            'https://discord.com/api/oauth2/authorize?client_id=1152379249928446074&permissions=1084479634496&scope=bot',
            ephemeral=True)

    @commands.slash_command()
    async def github(self, ctx: discord.ApplicationContext):
        await ctx.response.send_message(
            'https://github.com/ianbuergis/osuSwissBot',
            ephemeral=True)
