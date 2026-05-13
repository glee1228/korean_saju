"""월주(月柱) 계산기 — 절(節) 기준."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ..calendar.solar_term import SolarTermType
from ..calendar.solar_term_source import SolarTermSource
from .cheon_gan import CheonGan
from .gan_ji import GanJi
from .ji_ji import JiJi

# 12개 절(節) → 月支.
_JEOL_TO_BRANCH: dict[str, JiJi] = {
    "입춘": JiJi.IN,   "경칩": JiJi.MYO, "청명": JiJi.JIN, "입하": JiJi.SA,
    "망종": JiJi.O,    "소서": JiJi.MI,  "입추": JiJi.SIN, "백로": JiJi.YU,
    "한로": JiJi.SUL,  "입동": JiJi.HAE, "대설": JiJi.JA,  "소한": JiJi.CHUK,
}


class MonthPillar:
    """절기 기준 월주 계산기."""

    def __init__(self) -> None:
        raise TypeError("MonthPillar is a static utility class")

    @staticmethod
    def for_kst_moment(
        kst_moment: datetime,
        year_pillar: GanJi,
        solar_terms: SolarTermSource,
    ) -> GanJi:
        """입력 [kst_moment]의 월주."""
        utc = _kst_to_utc(kst_moment)
        last_jeol = solar_terms.term_at_or_before(utc, type=SolarTermType.JEOL)
        if last_jeol is None:
            raise RuntimeError(f"직전 절(節) 데이터 없음: {kst_moment}")
        month_branch = _JEOL_TO_BRANCH[last_jeol.name]
        month_stem = _stem_for_month(year_pillar.cheon_gan, month_branch)
        return GanJi(month_stem, month_branch)


def _stem_for_month(year_stem: CheonGan, month_branch: JiJi) -> CheonGan:
    """五虎遁法: monthStemIdx = (yearStemIdx * 2 + monthOrdinal + 2) mod 10."""
    ordinal = (month_branch.index - 2 + 12) % 12
    stem_idx = (year_stem.index * 2 + ordinal + 2) % 10
    return CheonGan.by_index(stem_idx)


def _kst_to_utc(kst: datetime) -> datetime:
    naive = kst.replace(tzinfo=None)
    as_utc_wall = datetime(
        naive.year, naive.month, naive.day,
        naive.hour, naive.minute, naive.second, naive.microsecond,
        tzinfo=UTC,
    )
    return as_utc_wall - timedelta(hours=9)
