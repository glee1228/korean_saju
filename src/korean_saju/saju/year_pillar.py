"""연주(年柱) 계산기 — 입춘(立春) 시각 기준."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ..calendar.solar_term_source import SolarTermSource
from .gan_ji import GanJi


class YearPillar:
    """입춘 기준 60갑자 연주."""

    def __init__(self) -> None:
        raise TypeError("YearPillar is a static utility class")

    @staticmethod
    def for_kst_moment(kst_moment: datetime, solar_terms: SolarTermSource) -> GanJi:
        """KST로 해석된 [kst_moment]의 연주 60갑자."""
        utc = _kst_to_utc(kst_moment)
        year = kst_moment.year
        ip_chun = solar_terms.get(year, "입춘")
        if ip_chun is None:
            raise RuntimeError(f"입춘 시각 데이터 없음: {year}")
        effective_year = year - 1 if utc < ip_chun.datetime else year
        return _ganji_for_year(effective_year)


def _ganji_for_year(year: int) -> GanJi:
    """입춘-기준 [year]의 60갑자. 검증: 1984=甲子(0), 1900=庚子(36), 2024=甲辰(40)."""
    return GanJi.by_index(((year - 4) % 60 + 60) % 60)


def _kst_to_utc(kst: datetime) -> datetime:
    """KST DateTime → UTC. naive datetime을 KST로 간주해 UTC로 변환."""
    naive = kst.replace(tzinfo=None)
    as_utc_wall = datetime(
        naive.year, naive.month, naive.day,
        naive.hour, naive.minute, naive.second, naive.microsecond,
        tzinfo=UTC,
    )
    return as_utc_wall - timedelta(hours=9)
