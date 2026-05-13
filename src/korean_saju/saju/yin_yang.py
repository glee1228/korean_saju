"""음양(陰陽)."""

from __future__ import annotations

from enum import Enum


class YinYang(Enum):
    YANG = ("陽", "양")
    EUM = ("陰", "음")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul
