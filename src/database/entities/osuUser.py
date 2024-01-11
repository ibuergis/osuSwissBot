from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .skin import Skin
from .base import Base


class OsuUser(Base):
    __tablename__ = "osuUser"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, unique=True)
    username: Mapped[str] = mapped_column(String[100])
    osuRank: Mapped[int] = mapped_column(nullable=True, default=None)
    maniaRank: Mapped[int] = mapped_column(nullable=True, default=None)
    taikoRank: Mapped[int] = mapped_column(nullable=True, default=None)
    catchRank: Mapped[int] = mapped_column(nullable=True, default=None)
    skin: Mapped[Skin] = mapped_column(ForeignKey('skin.id'))
    skinName: Mapped[str] = mapped_column(String[1000])
    country: Mapped[str] = mapped_column(String[2])
