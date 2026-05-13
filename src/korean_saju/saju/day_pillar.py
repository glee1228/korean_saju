"""일주(日柱) 계산기 — Julian Day 기반 60갑자 사이클.

기준점: 1900-01-31 KST = JD 2415050.5 (UTC midnight) = 甲辰 (index 40).
야자시/조자시 처리는 호출 측 (Saju.from_birth)에서 미리 보정한 date를 넘긴다.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ..calendar.julian_day import datetime_to_julian_day
from .gan_ji import GanJi

_REF_GANJI_INDEX = 40
_REF_JULIAN_DAY = 2415050.5


class DayPillar:
    """양력 calendar date → 일주 60갑자."""

    def __init__(self) -> None:
        raise TypeError("DayPillar is a static utility class")

    @staticmethod
    def for_date(date: datetime) -> GanJi:
        """양력 [date]의 일주. 시·분·초는 무시 (year/month/day만 사용)."""
        date_utc = datetime(date.year, date.month, date.day, tzinfo=UTC)
        jd = datetime_to_julian_day(date_utc)
        days_diff = round(jd - _REF_JULIAN_DAY)
        return GanJi.by_index(_REF_GANJI_INDEX + days_diff)
