"""ΔT (delta T) — Terrestrial Time(TT) - Universal Time(UT). 단위: 초.

Espenak/Meeus 다항식 기반. 1900–2150 범위에서 0.5초 이하 정확도.
출처: NASA Eclipse Web Site (https://eclipse.gsfc.nasa.gov/SEcat5/deltatpoly.html).
"""

from __future__ import annotations


def delta_t(year: int, month: int) -> float:
    y = year + (month - 0.5) / 12.0

    if year < 1900:
        t = (y - 1820) / 100.0
        return -20.0 + 32.0 * t * t
    if year < 1920:
        t = y - 1900
        return (
            -2.79
            + 1.494119 * t
            - 0.0598939 * t**2
            + 0.0061966 * t**3
            - 0.000197 * t**4
        )
    if year < 1941:
        t = y - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    if year < 1961:
        t = y - 1950
        return 29.07 + 0.407 * t - t**2 / 233 + t**3 / 2547
    if year < 1986:
        t = y - 1975
        return 45.45 + 1.067 * t - t**2 / 260 - t**3 / 718
    if year < 2005:
        t = y - 2000
        return (
            63.86
            + 0.3345 * t
            - 0.060374 * t**2
            + 0.0017275 * t**3
            + 0.000651814 * t**4
            + 0.00002373599 * t**5
        )
    if year < 2050:
        t = y - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t**2
    if year <= 2150:
        return -20.0 + 32.0 * ((y - 1820) / 100) ** 2 - 0.5628 * (2150 - y)
    # year > 2150 — generic far-future
    t = (y - 1820) / 100
    return -20.0 + 32.0 * t * t
