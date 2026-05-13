"""시주(時柱) 계산기 — 진태양시 보정 + 五鼠遁法."""

from __future__ import annotations

from datetime import datetime

from ..solar_time.solar_time_correction import SolarTimeCorrection
from .cheon_gan import CheonGan
from .gan_ji import GanJi
from .ji_ji import JiJi


class HourPillar:
    """시주 계산기."""

    def __init__(self) -> None:
        raise TypeError("HourPillar is a static utility class")

    @staticmethod
    def for_kst_moment(
        *,
        kst_moment: datetime,
        day_pillar: GanJi,
        longitude: float = SolarTimeCorrection.SEOUL_LONGITUDE,
    ) -> GanJi:
        """[kst_moment]에서 시주 계산. [day_pillar]의 일간으로 五鼠遁."""
        ast = SolarTimeCorrection.to_apparent_solar_time(kst_moment, longitude=longitude)
        hour_branch = _branch_for_ast_hour(ast.hour)
        time_stem = _stem_for_hour(day_pillar.cheon_gan, hour_branch)
        return GanJi(time_stem, hour_branch)


def _branch_for_ast_hour(hour: int) -> JiJi:
    """진태양시 hour(0–23) → 12지시. 23/0 → 子, 1–2 → 丑, ..."""
    if hour == 23 or hour == 0:
        return JiJi.JA
    return JiJi.by_index(((hour + 1) // 2) % 12)


def _stem_for_hour(day_stem: CheonGan, hour_branch: JiJi) -> CheonGan:
    """五鼠遁法: timeStemIdx = (dayStemIdx * 2 + hourBranchIdx) mod 10.

    검증: 갑/기日 자시=甲子, 을/경=丙子, 병/신=戊子, 정/임=庚子, 무/계=壬子.
    """
    stem_idx = (day_stem.index * 2 + hour_branch.index) % 10
    return CheonGan.by_index(stem_idx)
