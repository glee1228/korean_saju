"""오행(五行)."""

from __future__ import annotations

from enum import Enum


class OHaeng(Enum):
    MOK = ("木", "목")
    HWA = ("火", "화")
    TO = ("土", "토")
    GEUM = ("金", "금")
    SU = ("水", "수")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul
