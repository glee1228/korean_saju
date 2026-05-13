"""SajuAnalysis — 4기둥 위에 명리 derived (십신·십이운성 등) 계산 묶음.

``Saju`` (raw 4기둥) ↔ ``SajuAnalysis`` (derived). 분리해서 raw 데이터 무결성 유지.
시간 모름 케이스 (saju.hour_pillar is None) — hour position 자동 제외.
"""

from __future__ import annotations

from dataclasses import dataclass

from .gan_ji import GanJi
from .gyeokguk import GyeokgukCalculator, GyeokgukResult
from .ji_ji import JiJi
from .oegyeok import OegyeokAnalyzer, OegyeokResult
from .saju import Saju, SajuPosition
from .shipsin import Shipsin, ShipsinCalculator
from .sibisinsal import Sibisinsal, SibisinsalCalculator
from .sibiunseong import Sibiunseong, SibiunseongCalculator
from .sinsal import SinsalCalculator, SinsalDetection
from .xun_gong import XunGong
from .yongsin import YongsinDeriver, YongsinResult


@dataclass(frozen=True, slots=True)
class GongmangByPillar:
    """기준 기둥의 旬空 지지 2개 + 사주 내 매칭된 다른 위치."""

    basis_pillar: SajuPosition
    gongmang_branches: tuple[JiJi, JiJi]
    matched_positions: tuple[SajuPosition, ...]

    @property
    def has_match(self) -> bool:
        return bool(self.matched_positions)


class SajuAnalysis:
    """raw Saju 위에 명리 derived 분석을 lazy property로 제공."""

    __slots__ = ("saju",)

    def __init__(self, saju: Saju) -> None:
        self.saju = saju

    def pillar_at(self, pos: SajuPosition) -> GanJi | None:
        """hour_pillar는 시간 모름이면 None."""
        if pos is SajuPosition.YEAR:
            return self.saju.year_pillar
        if pos is SajuPosition.MONTH:
            return self.saju.month_pillar
        if pos is SajuPosition.DAY:
            return self.saju.day_pillar
        if pos is SajuPosition.HOUR:
            return self.saju.hour_pillar
        raise ValueError(f"unknown position: {pos}")

    @property
    def cheon_gan_shipsin(self) -> dict[SajuPosition, Shipsin]:
        """천간 십신 (일주 자신은 비견이라 제외)."""
        result: dict[SajuPosition, Shipsin] = {
            SajuPosition.YEAR: ShipsinCalculator.for_cheon_gan(
                self.saju.day_stem, self.saju.year_pillar.cheon_gan
            ),
            SajuPosition.MONTH: ShipsinCalculator.for_cheon_gan(
                self.saju.day_stem, self.saju.month_pillar.cheon_gan
            ),
        }
        if self.saju.hour_pillar is not None:
            result[SajuPosition.HOUR] = ShipsinCalculator.for_cheon_gan(
                self.saju.day_stem, self.saju.hour_pillar.cheon_gan
            )
        return result

    @property
    def ji_ji_shipsin(self) -> dict[SajuPosition, Shipsin]:
        """지지 십신 (본기 기준)."""
        result: dict[SajuPosition, Shipsin] = {}
        for pos in SajuPosition:
            pillar = self.pillar_at(pos)
            if pillar is None:
                continue
            result[pos] = ShipsinCalculator.for_ji_ji(self.saju.day_stem, pillar.ji_ji)
        return result

    @property
    def sibiunseong(self) -> dict[SajuPosition, Sibiunseong]:
        """십이운성."""
        result: dict[SajuPosition, Sibiunseong] = {}
        for pos in SajuPosition:
            pillar = self.pillar_at(pos)
            if pillar is None:
                continue
            result[pos] = SibiunseongCalculator.for_ji_ji(self.saju.day_stem, pillar.ji_ji)
        return result

    @property
    def sinsal(self) -> list[SinsalDetection]:
        """검출된 신살 (길신 + 흉신)."""
        return SinsalCalculator.detect(self.saju)

    @property
    def sibisinsal(self) -> dict[SajuPosition, Sibisinsal]:
        """12신살 — 일지 기준."""
        return self._sibisinsal_for_reference(self.saju.day_pillar.ji_ji)

    @property
    def sibisinsal_by_year(self) -> dict[SajuPosition, Sibisinsal]:
        """12신살 — 연지 기준 (보조)."""
        return self._sibisinsal_for_reference(self.saju.year_pillar.ji_ji)

    def _sibisinsal_for_reference(self, ref: JiJi) -> dict[SajuPosition, Sibisinsal]:
        result: dict[SajuPosition, Sibisinsal] = {}
        for pos in SajuPosition:
            pillar = self.pillar_at(pos)
            if pillar is None:
                continue
            result[pos] = SibisinsalCalculator.for_branch(ref, pillar.ji_ji)
        return result

    @property
    def jeonggyeok(self) -> GyeokgukResult:
        """정격 — 월지 투간 규칙."""
        return GyeokgukCalculator.determine(self.saju)

    @property
    def oegyeok(self) -> list[OegyeokResult]:
        """외격 — accepted만 점수 내림차순."""
        all_results = [r for r in OegyeokAnalyzer.analyze_all(self.saju) if r.is_accepted]
        all_results.sort(key=lambda r: r.score, reverse=True)
        return all_results

    @property
    def yongsin(self) -> YongsinResult:
        """용신 도출 (5오행을 用·喜·忌·仇·閑로 분류)."""
        return YongsinDeriver.derive(self.saju, self.oegyeok)

    @property
    def gongmang_by_pillar(self) -> dict[SajuPosition, GongmangByPillar]:
        """공망 — 일주 기준(표준) + 연주 기준(보조)."""
        result: dict[SajuPosition, GongmangByPillar] = {}
        for pos in (SajuPosition.DAY, SajuPosition.YEAR):
            pillar = self.pillar_at(pos)
            if pillar is None:
                continue
            kong = XunGong.kong_mang_for(pillar)
            matches: list[SajuPosition] = []
            for other in SajuPosition:
                if other is pos:
                    continue
                other_pillar = self.pillar_at(other)
                if other_pillar is None:
                    continue
                if other_pillar.ji_ji in kong:
                    matches.append(other)
            result[pos] = GongmangByPillar(
                basis_pillar=pos,
                gongmang_branches=kong,
                matched_positions=tuple(matches),
            )
        return result
