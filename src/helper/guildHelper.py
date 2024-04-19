import ossapi

from src.database.entities.discordUser import DiscordUser
from src.database.entities.guild import Guild
from src.helper.validator import Validator


class GuildHelper:

    validator: Validator

    def __init__(self, validator):
        self.validator = validator

    def setScoresChannel(self, guild: Guild, channelId: int | str, gamemode: ossapi.GameMode):
        if type(guild) is not Guild:
            raise ValueError('guild should be of Class: Guild')

        self.validator.isGamemode(gamemode, throw=True)

        guild.__setattr__(gamemode.name.lower() + 'ScoresChannel', channelId)
        return True

    def removeScoresChannel(self, guild: Guild, gamemode: ossapi.GameMode):
        if type(guild) is not Guild:
            raise ValueError('guild should be of Class: Guild')

        self.validator.isGamemode(gamemode, throw=True)

        guild.__setattr__(gamemode.name.lower() + 'ScoresChannel', None)
        return True

    def getScoresChannel(self, guild: Guild, gamemode: ossapi.GameMode):
        if type(guild) is not Guild:
            raise ValueError('guild should be of Class: Guild')

        self.validator.isGamemode(gamemode, throw=True)

        return guild.__getattribute__(gamemode.name.lower() + 'ScoresChannel')

    def addMentionForScores(self, guild: Guild, discordUser: DiscordUser, gamemode: ossapi.GameMode):
        if type(guild) is not Guild:
            raise ValueError('guild should be of Class: Guild')

        if type(discordUser) is not DiscordUser:
            raise ValueError('discordUser should be of Class: DiscordUser')

        self.validator.isGamemode(gamemode, throw=True)

        if discordUser in guild.__getattribute__(gamemode.name.lower() + 'MentionOnTopPlay'):
            return True

        guild.__getattribute__(gamemode.name.lower() + 'MentionOnTopPlay').append(discordUser)
        return True

    def removeMentionForScores(self, guild: Guild, discordUser: DiscordUser, gamemode: ossapi.GameMode):
        if type(guild) is not Guild:
            raise ValueError('guild should be of Class: Guild')

        if type(discordUser) is not DiscordUser:
            raise ValueError('discordUser should be of Class: DiscordUser')

        self.validator.isGamemode(gamemode, throw=True)

        if discordUser not in guild.__getattribute__(gamemode.name.lower() + 'MentionOnTopPlay'):
            return True

        guild.__getattribute__(gamemode.name.lower() + 'MentionOnTopPlay').remove(discordUser)
        return True

    def getMentionForScores(self, guild: Guild, gamemode: ossapi.GameMode):
        if type(guild) is not Guild:
            raise ValueError('guild should be of Class: Guild')

        self.validator.isGamemode(gamemode, throw=True)

        return guild.__getattribute__(gamemode.name.lower() + 'MentionOnTopPlay')
