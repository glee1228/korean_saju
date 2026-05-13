"""KASI 24절기 데이터 컨테이너 (2000–2027)."""

from __future__ import annotations

import json
from bisect import bisect_right
from datetime import datetime

from .solar_term import SolarTerm, SolarTermType


class KasiSolarTerms:
    """KASI 24절기 데이터(JSON) 파싱·검색.

    데이터 범위는 KASI Open API가 제공하는 2000–2027년. 그 외는 천문 계산 모듈로 보충.
    """

    __slots__ = ("_terms", "_term_times")

    def __init__(self, terms: list[SolarTerm]) -> None:
        sorted_terms = sorted(terms, key=lambda t: t.datetime)
        self._terms: tuple[SolarTerm, ...] = tuple(sorted_terms)
        self._term_times: tuple[datetime, ...] = tuple(t.datetime for t in sorted_terms)

    @classmethod
    def from_json(cls, json_string: str) -> KasiSolarTerms:
        data = json.loads(json_string)
        terms = [
            SolarTerm(
                year=t["year"],
                name=t["name"],
                datetime=_parse_iso_to_utc(t["datetime"]),
            )
            for t in data["terms"]
        ]
        return cls(terms)

    @property
    def terms(self) -> tuple[SolarTerm, ...]:
        return self._terms

    def terms_for_year(self, year: int) -> list[SolarTerm]:
        """특정 연도의 24절기 (1월 소한부터 12월 동지까지 순서)."""
        return [t for t in self._terms if t.year == year]

    def get(self, year: int, name: str) -> SolarTerm | None:
        for t in self._terms:
            if t.year == year and t.name == name:
                return t
        return None

    def term_at_or_before(
        self, moment: datetime, *, type: SolarTermType | None = None
    ) -> SolarTerm | None:
        if type is None:
            source = self._terms
            times = self._term_times
        else:
            source = tuple(t for t in self._terms if t.type is type)
            times = tuple(t.datetime for t in source)
        if not source:
            return None
        if moment < source[0].datetime:
            return None

        idx = bisect_right(times, moment) - 1
        if idx < 0:
            return None
        return source[idx]

    def term_after(
        self, moment: datetime, *, type: SolarTermType | None = None
    ) -> SolarTerm | None:
        source = self._terms if type is None else (t for t in self._terms if t.type is type)
        for t in source:
            if t.datetime > moment:
                return t
        return None

    @property
    def covered_range(self) -> tuple[datetime, datetime]:
        return (self._terms[0].datetime, self._terms[-1].datetime)


def _parse_iso_to_utc(s: str) -> datetime:
    """KASI 데이터의 비표준 ISO 8601 (minute=60·second=60 overflow) 허용 파싱."""
    from datetime import UTC, timedelta

    s_norm = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s_norm)
    except ValueError:
        dt, overflow_seconds = _parse_iso_with_overflow(s_norm)
        if overflow_seconds:
            dt = dt + timedelta(seconds=overflow_seconds)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)
    return dt


def _parse_iso_with_overflow(s: str) -> tuple[datetime, int]:
    """ISO 8601 문자열에서 분/초가 60인 경우 0으로 잘라 파싱하고 overflow 초를 별도 반환."""
    import re

    pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})(\.\d+)?([+-]\d{2}:?\d{2}|Z)?$"
    )
    m = pattern.match(s)
    if not m:
        raise ValueError(f"unrecognized ISO 8601: {s}")
    date_part, hh, mm, ss, frac, tz = m.groups()
    overflow = 0
    h, mi, se = int(hh), int(mm), int(ss)
    if se >= 60:
        overflow += se - 59
        se = 59
    if mi >= 60:
        overflow += (mi - 59) * 60
        mi = 59
    if h >= 24:
        overflow += (h - 23) * 3600
        h = 23
    rebuilt = f"{date_part}T{h:02d}:{mi:02d}:{se:02d}{frac or ''}{tz or ''}"
    return datetime.fromisoformat(rebuilt), overflow
