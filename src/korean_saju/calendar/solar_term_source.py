"""통합 24절기 lookup — KASI(2000–2027) 우선, 그 외는 Meeus 천문 계산."""

from __future__ import annotations

from datetime import UTC, datetime

from .kasi_solar_terms import KasiSolarTerms
from .solar_term import SolarTerm, SolarTermType
from .solar_term_calculator import SolarTermCalculator


class SolarTermSource:
    """KASI 우선, 범위 밖이면 천문 계산기로 fallback하는 통합 절기 source."""

    __slots__ = ("_kasi",)

    def __init__(self, kasi: KasiSolarTerms) -> None:
        self._kasi = kasi

    def terms_for_year(self, year: int) -> list[SolarTerm]:
        from_kasi = self._kasi.terms_for_year(year)
        if len(from_kasi) == 24:
            return from_kasi
        return SolarTermCalculator.terms_for_year(year)

    def get(self, year: int, name: str) -> SolarTerm | None:
        from_kasi = self._kasi.get(year, name)
        if from_kasi is not None:
            return from_kasi
        computed = SolarTermCalculator.terms_for_year(year)
        for t in computed:
            if t.name == name:
                return t
        return None

    def term_at_or_before(
        self, moment: datetime, *, type: SolarTermType | None = None
    ) -> SolarTerm | None:
        candidates = self._span_candidates(moment)
        result: SolarTerm | None = None
        for t in candidates:
            if type is not None and t.type is not type:
                continue
            if t.datetime > moment:
                break
            result = t
        return result

    def term_after(
        self, moment: datetime, *, type: SolarTermType | None = None
    ) -> SolarTerm | None:
        candidates = self._span_candidates(moment)
        for t in candidates:
            if type is not None and t.type is not type:
                continue
            if t.datetime > moment:
                return t
        return None

    def _span_candidates(self, moment: datetime) -> list[SolarTerm]:
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=UTC)
        year = moment.astimezone(UTC).year
        candidates: list[SolarTerm] = []
        candidates.extend(self.terms_for_year(year - 1))
        candidates.extend(self.terms_for_year(year))
        candidates.extend(self.terms_for_year(year + 1))
        candidates.sort(key=lambda t: t.datetime)
        return candidates

    def accuracy_for(self, year: int) -> str:
        """데이터 소스 정확도 등급 ("kasi" 분 단위 / "computed" ±15분)."""
        return "kasi" if 2000 <= year <= 2027 else "computed"
