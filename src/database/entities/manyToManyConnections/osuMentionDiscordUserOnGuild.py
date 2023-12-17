from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from ..base import Base


class OsuMentionDiscordUserOnGuild(Base):
    __tablename__ = 'osuMentionDiscordUserOnGuild'

    discordUser: Mapped[int] = mapped_column(ForeignKey('discordUser.id'), primary_key=True)
    guild: Mapped[int] = mapped_column(ForeignKey('guild.id'), primary_key=True)
