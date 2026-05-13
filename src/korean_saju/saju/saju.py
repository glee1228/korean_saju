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

        **자시(子時) 영역 — 모두 진태양시(AST) 기준**

        - **야자시(夜子時)**: AST 23:00–24:00 (당일 자시 영역).
        - **조자시(朝子時)**: AST 00:00–01:00 (다음날 자시 영역).
        - 시주 자시는 두 경우 모두 **다음날 일간** 五鼠遁
          (야자시 다음날 일간 = 조자시 그날 일간으로 동일).

        **일주(日柱)** 처리 — ``yaja_si_separated``에 따라 분기:

        - True (분리법, 한국 명리 표준, **기본**):
          야자시는 AST 당일 일주, 조자시는 자연스럽게 AST 다음날 일주.
        - False (정자시 단일·일자시): 야자시도 다음날 일주로 통합.

        일주·시주는 **AST 캘린더 날짜** 기준으로 계산해야 한다. KST 날짜
        기준으로 하면 longitude 보정으로 KST는 자정을 넘었지만 AST는 아직
        어제인 경우 (예: KST 1990-01-02 00:10 서울 → AST 23:38) 일주가
        하루 어긋난다.

        예: 1994-04-28 23:40 KST 서울(−32분) → AST 23:08 (야자시)
            - ``yaja_si_separated=True``  → 갑신일 + 병자시
            - ``yaja_si_separated=False`` → 을유일 + 병자시
        """
        # 연주·월주는 절대 시각(UTC) 기준 — KST moment 그대로.
        year = YearPillar.for_kst_moment(kst_moment, solar_terms)
        month = MonthPillar.for_kst_moment(kst_moment, year, solar_terms)

        # 일주·시주는 AST 기준.
        ast = SolarTimeCorrection.to_apparent_solar_time(kst_moment, longitude=longitude)
        ast_date = datetime(ast.year, ast.month, ast.day)

        # 자시(子時) 영역 판별 (AST 기준).
        is_yaja_si = ast.hour == 23  # AST 23:00–23:59
        # 조자시(AST 00:00–00:59)는 ast_date가 이미 다음날을 가리키므로 별도 분기 불필요.

        # 일주: 야자시 + 단일자시 모드에서만 다음날로 advance.
        #   - 분리법(기본): 항상 AST 캘린더 날짜 그대로.
        #   - 단일자시: 야자시도 강제로 다음날로 통합.
        if is_yaja_si and not yaja_si_separated:
            date_for_day = ast_date + timedelta(days=1)
        else:
            date_for_day = ast_date
        day = DayPillar.for_date(date_for_day)

        # 시주: 자시는 항상 다음날 일간 五鼠遁.
        #   - 야자시: AST 당일 + 1 = 다음날 일간
        #   - 조자시: 일주가 이미 AST 다음날 = 동일한 일간
        hour: GanJi | None = None
        if hour_known:
            if is_yaja_si:
                hour_day_pillar = DayPillar.for_date(ast_date + timedelta(days=1))
            else:
                hour_day_pillar = day
            hour = HourPillar.for_kst_moment(
                kst_moment=kst_moment,
                day_pillar=hour_day_pillar,
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
