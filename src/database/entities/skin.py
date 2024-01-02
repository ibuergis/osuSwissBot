from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Skin(Base):
    __tablename__ = "skin"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    hash: Mapped[str] = mapped_column(String[64])
    osuUsers: Mapped[List["OsuUser"]] = relationship()
