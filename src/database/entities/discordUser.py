from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base

class DiscordUser(Base):
    __tablename__ = "discordUser"

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[str] = mapped_column(String[100], unique=True)
