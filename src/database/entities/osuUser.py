from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class OsuUser(Base):
    __tablename__ = "osuUser"

    userId: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, unique=True)
    username: Mapped[str] = mapped_column(String[100])
    osuRank: Mapped[int]
    maniaRank: Mapped[int]
    taikoRank: Mapped[int]
    catchRank: Mapped[int]
    country: Mapped[str] = mapped_column(String[2])
