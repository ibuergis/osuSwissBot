import discord
from database.guildCalls import Guild



def memberIsUploader(uploaderRole: int|None, member: discord.Member):
    if member.guild_permissions.administrator:
        return True
    
    for role in member.roles:
        print(role.id, uploaderRole)
        if role.id == uploaderRole:
            return True
        
    return False
