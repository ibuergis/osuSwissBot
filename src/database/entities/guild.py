from typing import List

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base
from .discordUser import DiscordUser
from .manyToManyConnections.osuMentionDiscordUserOnGuild import OsuMentionDiscordUserOnGuild
from .manyToManyConnections.maniaMentionDiscordUserOnGuild import ManiaMentionDiscordUserOnGuild
from .manyToManyConnections.taikoMentionDiscordUserOnGuild import TaikoMentionDiscordUserOnGuild
from .manyToManyConnections.catchMentionDiscordUserOnGuild import CatchMentionDiscordUserOnGuild

class Guild(Base):
    __tablename__ = "guild"

    id: Mapped[int] = mapped_column(primary_key=True)
    guildId: Mapped[str] = mapped_column(String[100], unique=True)
    osuScoresChannel: Mapped[str] = mapped_column(String[100], nullable=True, default=None)
    maniaScoresChannel: Mapped[str] = mapped_column(String[100], nullable=True, default=None)
    taikoScoresChannel: Mapped[str] = mapped_column(String[100], nullable=True, default=None)
    catchScoresChannel: Mapped[str] = mapped_column(String[100], nullable=True, default=None)
    osuMentionOnTopPlay: Mapped[List[DiscordUser]] = relationship(DiscordUser, OsuMentionDiscordUserOnGuild.__tablename__)
    maniaMentionOnTopPlay: Mapped[List[DiscordUser]] = relationship(DiscordUser, ManiaMentionDiscordUserOnGuild.__tablename__)
    taikoMentionOnTopPlay: Mapped[List[DiscordUser]] = relationship(DiscordUser, TaikoMentionDiscordUserOnGuild.__tablename__)
    catchMentionOnTopPlay: Mapped[List[DiscordUser]] = relationship(DiscordUser, CatchMentionDiscordUserOnGuild.__tablename__)
