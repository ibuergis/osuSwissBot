import discord

def userIsUploader(guild: discord, user: discord.User, roleId: int):
    return roleId in guild['uploaders']
