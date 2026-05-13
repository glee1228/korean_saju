"""24절기 시각을 천문 계산으로 산출.

태양 황경이 정해진 각도(15° 간격)에 도달하는 UT 시각을 Newton 반복으로 역산.
데이터 갭(KASI Open API의 1900-1999, 2028-2100 부재 구간) 보완용.
"""

from __future__ import annotations

from datetime import UTC, datetime

from .delta_t import delta_t
from .julian_day import datetime_to_julian_day, julian_day_to_datetime
from .solar_term import SolarTerm
from .sun_position import sun_apparent_longitude

# 24절기 → 태양 황경 (도). 정통 명리 기준.
_TERM_LONGITUDES: dict[str, float] = {
    "소한": 285, "대한": 300, "입춘": 315, "우수": 330, "경칩": 345,
    "춘분": 0,   "청명": 15,  "곡우": 30,  "입하": 45,  "소만": 60,
    "망종": 75,  "하지": 90,  "소서": 105, "대서": 120, "입추": 135,
    "처서": 150, "백로": 165, "추분": 180, "한로": 195, "상강": 210,
    "입동": 225, "소설": 240, "대설": 255, "동지": 270,
}

# 24절기 → 양력 근사 (월, 일). Newton 반복 시작점.
_APPROX_MONTH_DAY: dict[str, tuple[int, int]] = {
    "소한": (1, 5),  "대한": (1, 20),
    "입춘": (2, 4),  "우수": (2, 19),
    "경칩": (3, 5),  "춘분": (3, 20),
    "청명": (4, 5),  "곡우": (4, 20),
    "입하": (5, 5),  "소만": (5, 21),
    "망종": (6, 5),  "하지": (6, 21),
    "소서": (7, 7),  "대서": (7, 22),
    "입추": (8, 7),  "처서": (8, 23),
    "백로": (9, 7),  "추분": (9, 23),
    "한로": (10, 8), "상강": (10, 23),
    "입동": (11, 7), "소설": (11, 22),
    "대설": (12, 7), "동지": (12, 21),
}

ORDERED_NAMES: tuple[str, ...] = (
    "소한", "대한", "입춘", "우수", "경칩", "춘분",
    "청명", "곡우", "입하", "소만", "망종", "하지",
    "소서", "대서", "입추", "처서", "백로", "추분",
    "한로", "상강", "입동", "소설", "대설", "동지",
)


class SolarTermCalculator:
    """24절기 천문 계산기."""

    @staticmethod
    def terms_for_year(year: int) -> list[SolarTerm]:
        """주어진 양력 연도의 24절기 시각(UTC). 정밀도: 분 이내 (KASI 기준)."""
        result: list[SolarTerm] = []
        for name in ORDERED_NAMES:
            lon = _TERM_LONGITUDES[name]
            approx_month, approx_day = _APPROX_MONTH_DAY[name]
            dt = _find_crossing(year, lon, approx_month, approx_day)
            result.append(SolarTerm(year=year, name=name, datetime=dt))
        return result


def _find_crossing(
    year: int, target_lon: float, approx_month: int, approx_day: int
) -> datetime:
    """황경 [target_lon]도가 (year, approx_month, approx_day) 부근에서 도달하는 UT 시각."""
    jd_ut = datetime_to_julian_day(datetime(year, approx_month, approx_day, tzinfo=UTC))

    DAILY_MOTION = 0.9856  # °/day
    TOLERANCE = 1e-5  # °
    MAX_ITER = 30

    for _ in range(MAX_ITER):
        dt = delta_t(year, approx_month)
        jd_tt = jd_ut + dt / 86400.0

        lon = sun_apparent_longitude(jd_tt)
        diff = target_lon - lon
        if diff > 180:
            diff -= 360
        if diff < -180:
            diff += 360

        if abs(diff) < TOLERANCE:
            break

        jd_ut += diff / DAILY_MOTION

    return julian_day_to_datetime(jd_ut)
