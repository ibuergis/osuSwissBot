import discord

from discord.ext.commands import User

from src.database import Guild;

def userIsUploader(guild: discord, user: discord.User, roleId: int):
    return roleId in guild['uploaders']
