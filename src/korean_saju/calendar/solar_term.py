"""24절기 (節氣) 값 객체."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SolarTermType(Enum):
    """절(節, 월의 시작점) vs 기(氣, 월의 중간점)."""

    JEOL = ("節", "절")
    GI = ("氣", "기")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul


_JEOL_NAMES: frozenset[str] = frozenset({
    "입춘", "경칩", "청명", "입하", "망종", "소서",
    "입추", "백로", "한로", "입동", "대설", "소한",
})


@dataclass(frozen=True, slots=True)
class SolarTerm:
    year: int
    name: str
    datetime: datetime  # UTC

    @property
    def type(self) -> SolarTermType:
        return SolarTermType.JEOL if self.name in _JEOL_NAMES else SolarTermType.GI

    def __str__(self) -> str:
        return f"{self.year} {self.name} ({self.datetime.isoformat()})"
