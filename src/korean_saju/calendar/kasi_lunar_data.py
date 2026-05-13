"""KASI 음양력 데이터(JSON) 파싱·검색 (1900–2050)."""

from __future__ import annotations

import json
from bisect import bisect_right
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from .lunar_date import LunarDate


@dataclass(frozen=True, slots=True)
class LunarMonthRecord:
    """음력 월의 시작일 + KASI 계산 60갑자 (일진/세차/월건) 묶음."""

    year: int
    month: int
    leap: bool
    start_solar: datetime  # UTC midnight, date-only semantics
    iljin: str  # 일진 (해당 월 1일의 60갑자)
    secha: str  # 세차 (해당 음력 연도의 60갑자)
    wolgeon: str  # 월건 (해당 월의 60갑자, 윤월은 빈 문자열)
    julian_day: int


class KasiLunarData:
    """KASI 음양력 데이터 컨테이너."""

    __slots__ = ("_months", "_starts")

    def __init__(self, months: list[LunarMonthRecord]) -> None:
        sorted_months = sorted(months, key=lambda m: m.start_solar)
        self._months: tuple[LunarMonthRecord, ...] = tuple(sorted_months)
        self._starts: tuple[datetime, ...] = tuple(m.start_solar for m in sorted_months)

    @classmethod
    def from_json(cls, json_string: str) -> KasiLunarData:
        data = json.loads(json_string)
        months: list[LunarMonthRecord] = []
        for m in data["months"]:
            solar_str = m["startSolar"]
            months.append(
                LunarMonthRecord(
                    year=m["year"],
                    month=m["month"],
                    leap=m["leap"],
                    start_solar=datetime.fromisoformat(f"{solar_str}T00:00:00+00:00"),
                    iljin=m.get("iljin") or "",
                    secha=m.get("secha") or "",
                    wolgeon=m.get("wolgeon") or "",
                    julian_day=m["julianDay"],
                )
            )
        return cls(months)

    @property
    def months(self) -> tuple[LunarMonthRecord, ...]:
        return self._months

    def solar_to_lunar(self, solar: datetime | LunarDate) -> LunarDate | None:
        """양력 → 음력. year/month/day만 참조 (시간·timezone 무시). 범위 밖이면 None."""
        if not self._months:
            return None
        if isinstance(solar, LunarDate):
            raise TypeError("solar_to_lunar expects a datetime, not LunarDate")
        date_utc = datetime(solar.year, solar.month, solar.day, tzinfo=UTC)
        if date_utc < self._months[0].start_solar:
            return None
        max_bound = self._months[-1].start_solar + timedelta(days=30)
        if date_utc > max_bound:
            return None

        idx = bisect_right(self._starts, date_utc) - 1
        if idx < 0:
            return None
        m = self._months[idx]
        day_diff = (date_utc - m.start_solar).days
        return LunarDate(
            year=m.year, month=m.month, day=day_diff + 1, is_leap=m.leap
        )

    def lunar_to_solar(
        self,
        *,
        year: int,
        month: int,
        day: int,
        is_leap: bool = False,
    ) -> datetime | None:
        """음력 → 양력. 윤달 없거나 day 초과면 None. 범위 밖도 None.

        반환값은 UTC 자정의 datetime.
        """
        if day < 1:
            return None
        target_idx: int | None = None
        for i, m in enumerate(self._months):
            if m.year == year and m.month == month and m.leap == is_leap:
                target_idx = i
                break
        if target_idx is None:
            return None
        target = self._months[target_idx]
        if target_idx + 1 < len(self._months):
            next_start = self._months[target_idx + 1].start_solar
        else:
            next_start = target.start_solar + timedelta(days=30)
        month_len = (next_start - target.start_solar).days
        if day > month_len:
            return None
        return target.start_solar + timedelta(days=day - 1)

    def has_leap_month(self, year: int, month: int) -> bool:
        return any(
            m.year == year and m.month == month and m.leap for m in self._months
        )

    def month_of(self, solar: datetime) -> LunarMonthRecord | None:
        if not self._months:
            return None
        date_utc = datetime(solar.year, solar.month, solar.day, tzinfo=UTC)
        if date_utc < self._months[0].start_solar:
            return None
        idx = bisect_right(self._starts, date_utc) - 1
        if idx < 0:
            return None
        return self._months[idx]

    @property
    def covered_solar_range(self) -> tuple[datetime, datetime]:
        return (
            self._months[0].start_solar,
            self._months[-1].start_solar + timedelta(days=30),
        )
