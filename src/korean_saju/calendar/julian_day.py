"""Julian Day (JD) ↔ datetime 변환.

Meeus, Astronomical Algorithms, Chapter 7.
Gregorian 달력 기준 (1582-10-15 이후). 사용 범위(1900–2150)는 모두 Gregorian.
"""

from __future__ import annotations

from datetime import UTC, datetime


def datetime_to_julian_day(utc: datetime) -> float:
    """UTC datetime → Julian Day (소수 포함)."""
    if utc.tzinfo is None or utc.utcoffset() is None or utc.utcoffset().total_seconds() != 0:
        raise ValueError("datetime_to_julian_day requires a UTC datetime")
    y = utc.year
    m = utc.month
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    day_with_fraction = utc.day + (
        utc.hour * 3600 + utc.minute * 60 + utc.second + utc.microsecond / 1e6
    ) / 86400.0
    return (
        int(365.25 * (y + 4716))
        + int(30.6001 * (m + 1))
        + day_with_fraction
        + b
        - 1524.5
    )


def julian_day_to_datetime(jd: float) -> datetime:
    """Julian Day → UTC datetime."""
    z = int(jd + 0.5)
    f = (jd + 0.5) - z

    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4

    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)

    day_with_fraction = b - d - int(30.6001 * e) + f
    day = int(day_with_fraction)
    day_frac = day_with_fraction - day

    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    total_micros = round(day_frac * 86400 * 1e6)
    hour, rem = divmod(total_micros, 3600 * 1_000_000)
    minute, rem = divmod(rem, 60 * 1_000_000)
    second, micros = divmod(rem, 1_000_000)

    return datetime(year, month, day, hour, minute, second, micros, tzinfo=UTC)
