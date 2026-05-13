"""지장간(地藏干) — 지지 안에 숨은 천간 + 역할."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cheon_gan import CheonGan


class JiJangGanRole(Enum):
    YEOGI = ("餘氣", "여기")
    JUNGGI = ("中氣", "중기")
    BONGI = ("本氣", "본기")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul


@dataclass(frozen=True, slots=True)
class JiJangGanComponent:
    stem: CheonGan
    role: JiJangGanRole
