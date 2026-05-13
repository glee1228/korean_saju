"""대운(大運) — 10년 단위 운세 흐름.

규칙:
  1. 방향: 양남(연간양·남) + 음녀(연간음·여) = 순행. 음남 + 양녀 = 역행.
  2. 시작 갑자: 월주의 다음 60갑자(순행) 또는 이전(역행).
  3. 시작 나이: 출생~다음 절(順) 또는 직전 절(逆)까지의 일수 / 3.
  4. 10년 단위로 갑자가 한 단계씩 순행/역행.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

from ..calendar.solar_term import SolarTermType
from ..calendar.solar_term_source import SolarTermSource
from .gan_ji import GanJi
from .saju import Saju


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass(frozen=True, slots=True)
class DaewoonEntry:
    """대운 한 단위 (10년)."""

    start_age: int
    gan_ji: GanJi
    start_months_offset: int = 0  # 첫 entry만 의미 있음 (0–11).

    def __str__(self) -> str:
        age = (
            f"{self.start_age}세 {self.start_months_offset}개월"
            if self.start_months_offset > 0
            else f"{self.start_age}세"
        )
        return f"{age} {self.gan_ji.hanja}"


@dataclass(frozen=True, slots=True)
class Daewoon:
    """대운 시퀀스."""

    entries: list[DaewoonEntry] = field(default_factory=list)
    forward: bool = True  # 순행/역행
    days_to_boundary: float = 0.0  # 첫 대운 시작까지의 일수 (디버그/표시용)

    @classmethod
    def compute(
        cls,
        *,
        saju: Saju,
        gender: Gender,
        solar_terms: SolarTermSource,
        count: int = 10,
    ) -> Daewoon:
        """[saju] + [gender]로 대운 계산. count만큼의 10년 단위 엔트리."""
        year_stem_is_yang = saju.year_pillar.cheon_gan.is_yang
        forward = (year_stem_is_yang and gender is Gender.MALE) or (
            not year_stem_is_yang and gender is Gender.FEMALE
        )

        birth_utc = _kst_to_utc(saju.kst_moment)
        if forward:
            nxt = solar_terms.term_after(birth_utc, type=SolarTermType.JEOL)
            if nxt is None:
                raise RuntimeError(f"다음 절(節) 데이터 없음: {saju.kst_moment}")
            days_to_boundary = (nxt.datetime - birth_utc).total_seconds() / 86400.0
        else:
            prev = solar_terms.term_at_or_before(birth_utc, type=SolarTermType.JEOL)
            if prev is None:
                raise RuntimeError(f"직전 절(節) 데이터 없음: {saju.kst_moment}")
            days_to_boundary = (birth_utc - prev.datetime).total_seconds() / 86400.0

        start_age_float = days_to_boundary / 3.0
        start_age_years = int(start_age_float)
        months_remainder = round((start_age_float - start_age_years) * 12)

        month_idx = saju.month_pillar.index
        cur_idx = month_idx + 1 if forward else month_idx - 1

        entries: list[DaewoonEntry] = []
        for i in range(count):
            entries.append(
                DaewoonEntry(
                    start_age=start_age_years + i * 10,
                    gan_ji=GanJi.by_index(cur_idx),
                    start_months_offset=months_remainder if i == 0 else 0,
                )
            )
            cur_idx += 1 if forward else -1

        return cls(entries=entries, forward=forward, days_to_boundary=days_to_boundary)


def _kst_to_utc(kst: datetime) -> datetime:
    naive = kst.replace(tzinfo=None)
    as_utc_wall = datetime(
        naive.year, naive.month, naive.day,
        naive.hour, naive.minute, naive.second, naive.microsecond,
        tzinfo=UTC,
    )
    return as_utc_wall - timedelta(hours=9)
