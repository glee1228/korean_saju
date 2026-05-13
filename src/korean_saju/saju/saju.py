"""사주(四柱) — 4기둥 묶음 + 통합 계산기.

야자시(夜子時) / 조자시(朝子時) 분리법은 ``Saju.from_birth(yaja_si_separated=...)`` 옵션으로 토글.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from ..calendar.solar_term_source import SolarTermSource
from ..solar_time.solar_time_correction import SolarTimeCorrection
from .cheon_gan import CheonGan
from .day_pillar import DayPillar
from .gan_ji import GanJi
from .hour_pillar import HourPillar
from .month_pillar import MonthPillar
from .year_pillar import YearPillar


class SajuPosition(Enum):
    """4기둥 위치."""

    YEAR = ("年", "년")
    MONTH = ("月", "월")
    DAY = ("日", "일")
    HOUR = ("時", "시")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul


@dataclass(frozen=True, slots=True)
class Saju:
    """사주 4기둥 + 부가 정보."""

    year_pillar: GanJi
    month_pillar: GanJi
    day_pillar: GanJi
    hour_pillar: GanJi | None  # 시간 모름이면 None
    kst_moment: datetime
    longitude: float

    @property
    def day_stem(self) -> CheonGan:
        """일간(日干, 본명 — 명리 해석의 기준)."""
        return self.day_pillar.cheon_gan

    @classmethod
    def from_birth(
        cls,
        *,
        kst_moment: datetime,
        solar_terms: SolarTermSource,
        longitude: float = SolarTimeCorrection.SEOUL_LONGITUDE,
        hour_known: bool = True,
        yaja_si_separated: bool = True,
    ) -> Saju:
        """출생 시각·경도로 사주 계산.

        Args:
            kst_moment: 출생 시각 (KST 해석). naive 또는 tz-aware 모두 허용.
            solar_terms: 절기 source (KASI+천문 fallback).
            longitude: 출생지 경도 (동경 +, 서경 −). 기본 서울.
            hour_known: False면 ``hour_pillar=None``. 3주만 의미 있음.
            yaja_si_separated: 야자시(夜子時) 분리법 토글.

        **야자시(夜子時) — 한국 명리 표준 분리법, boundary = 진태양시 23:00**

        - 진태양시 23:00–24:00 = 야자시 영역.
        - 시주(時柱)는 항상 다음날 일간 기준으로 五鼠遁 (子時는 새 사이클).
        - 일주(日柱)는 ``yaja_si_separated``에 따라 분기:
            - True (야자시 분리법, **기본**): 일주 = **그날** (자정 안 지났음)
            - False (정자시 단일·일자시): 일주 = **다음날** (자정 후처럼 처리)

        예: 1994-04-28 23:40 KST 서울(−32분) → 진태양시 23:08
            - ``yaja_si_separated=True`` → 갑신일 + 병자시 (을 일간 자시)
            - ``yaja_si_separated=False`` → 을유일 + 병자시
        """
        year = YearPillar.for_kst_moment(kst_moment, solar_terms)
        month = MonthPillar.for_kst_moment(kst_moment, year, solar_terms)

        # 야자시 검사: 진태양시 기준 (시주 결정과 동일 기준). boundary = 23:00.
        ast = SolarTimeCorrection.to_apparent_solar_time(kst_moment, longitude=longitude)
        is_after_2300 = ast.hour == 23

        # 일주: yaja_si_separated 분기.
        if is_after_2300 and not yaja_si_separated:
            date_for_day = kst_moment + timedelta(days=1)
        else:
            date_for_day = kst_moment
        day = DayPillar.for_date(date_for_day)

        # 시주: 진태양시 23:00 이후면 항상 다음날 일간 기준 (子時 새 사이클).
        hour: GanJi | None = None
        if hour_known:
            if is_after_2300:
                day_for_hour = DayPillar.for_date(kst_moment + timedelta(days=1))
            else:
                day_for_hour = day
            hour = HourPillar.for_kst_moment(
                kst_moment=kst_moment,
                day_pillar=day_for_hour,
                longitude=longitude,
            )

        return cls(
            year_pillar=year,
            month_pillar=month,
            day_pillar=day,
            hour_pillar=hour,
            kst_moment=kst_moment,
            longitude=longitude,
        )

    def __str__(self) -> str:
        hour = str(self.hour_pillar) if self.hour_pillar is not None else "時?"
        return f"{self.year_pillar} {self.month_pillar} {self.day_pillar} {hour}"
