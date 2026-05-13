"""세운(歲運) — 1년 단위 운세. 입춘 절입 기준 연주 60갑자."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..calendar.solar_term_source import SolarTermSource
from .gan_ji import GanJi
from .saju import Saju
from .year_pillar import YearPillar


@dataclass(frozen=True, slots=True)
class SewoonEntry:
    year: int  # 양력 연도
    age: int  # 만 나이
    gan_ji: GanJi

    def __str__(self) -> str:
        return f"{self.year}년 ({self.age}세) {self.gan_ji.hanja}"


class Sewoon:
    """세운 계산기 (정적 메서드)."""

    def __init__(self) -> None:
        raise TypeError("Sewoon is a static utility class")

    @staticmethod
    def compute(
        *,
        saju: Saju,
        solar_terms: SolarTermSource,
        center_year: int,
        years_back: int = 5,
        years_forward: int = 15,
    ) -> list[SewoonEntry]:
        """[center_year] 기준 [years_back] ~ [years_forward] 범위 세운."""
        birth_year = saju.kst_moment.year
        result: list[SewoonEntry] = []
        for y in range(center_year - years_back, center_year + years_forward + 1):
            # 입춘 후 시점(6월 1일)으로 연주 계산.
            gan_ji = YearPillar.for_kst_moment(
                datetime(y, 6, 1), solar_terms
            )
            result.append(
                SewoonEntry(year=y, age=y - birth_year, gan_ji=gan_ji)
            )
        return result
