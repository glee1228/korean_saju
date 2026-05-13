"""태양의 겉보기 황경(apparent ecliptic longitude) 계산.

Meeus, Astronomical Algorithms, Chapter 25 (lower-precision formula).
정확도: ±0.01° (= 시간으로 약 0.6분).
"""

from __future__ import annotations

import math


def sun_apparent_longitude(jd_tt: float) -> float:
    """주어진 Julian Day TT(Terrestrial Time)에서 태양의 겉보기 황경 (도, 0–360)."""
    t = (jd_tt - 2451545.0) / 36525.0

    # Geometric mean longitude of the Sun (deg)
    l0 = _norm360(280.46646 + t * (36000.76983 + t * 0.0003032))

    # Mean anomaly of the Sun (deg)
    m = 357.52911 + t * (35999.05029 - t * 0.0001537)
    m_rad = math.radians(m)

    # Equation of center (deg)
    c = (
        (1.914602 - t * (0.004817 + t * 0.000014)) * math.sin(m_rad)
        + (0.019993 - t * 0.000101) * math.sin(2 * m_rad)
        + 0.000289 * math.sin(3 * m_rad)
    )

    # True (geometric) longitude
    true_lon = l0 + c

    # Correction for nutation and aberration → apparent longitude
    omega = 125.04 - 1934.136 * t
    apparent_lon = true_lon - 0.00569 - 0.00478 * math.sin(math.radians(omega))

    return _norm360(apparent_lon)


def _norm360(deg: float) -> float:
    x = deg % 360
    if x < 0:
        x += 360
    return x
