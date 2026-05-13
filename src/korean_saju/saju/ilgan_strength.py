"""일간 강약 — 자평 표준 득령·득지·득세 + 합충형파해 보정."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cheon_gan import CheonGan
from .hapchung import HapChungAnalyzer
from .ji_jang_gan import JiJangGanRole
from .ji_ji import JiJi
from .o_haeng import OHaeng
from .saju import Saju


class IlganStrengthLevel(Enum):
    GEUKSINKANG = ("極身強", "극신강")
    SINKANG = ("身強", "신강")
    JUNGHWA = ("中和", "중화")
    SINYAK = ("身弱", "신약")
    GEUKSINYAK = ("極身弱", "극신약")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul


@dataclass(frozen=True, slots=True)
class _DeukWeight:
    bigeop: int
    inseong: int
    siksang: int
    jaeseong: int
    gwansal: int


_MONTH_BRANCH_W = _DeukWeight(bigeop=25, inseong=20, siksang=3, jaeseong=-10, gwansal=-18)
_DAY_BRANCH_W = _DeukWeight(bigeop=15, inseong=12, siksang=3, jaeseong=-5, gwansal=-5)
_OTHER_BRANCH_W = _DeukWeight(bigeop=6, inseong=5, siksang=2, jaeseong=-3, gwansal=-3)


@dataclass(frozen=True, slots=True)
class IlganStrengthBreakdown:
    deuk_ryeong: int
    deuk_ji: int
    deuk_sae: int
    hap_chung_adjust: int
    total: int  # 0~100 clamp
    level: IlganStrengthLevel
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.level.hangul} ({self.total}점) — "
            f"득령 {self.deuk_ryeong} + 득지 {self.deuk_ji} + "
            f"득세 {self.deuk_sae} + 합충 {self.hap_chung_adjust}"
        )


_GEN_CHAIN = (OHaeng.MOK, OHaeng.HWA, OHaeng.TO, OHaeng.GEUM, OHaeng.SU)
_OVR_CHAIN = (OHaeng.MOK, OHaeng.TO, OHaeng.SU, OHaeng.HWA, OHaeng.GEUM)


def _generates(a: OHaeng, b: OHaeng) -> bool:
    return (_GEN_CHAIN.index(a) + 1) % 5 == _GEN_CHAIN.index(b)


def _overcomes(a: OHaeng, b: OHaeng) -> bool:
    return (_OVR_CHAIN.index(a) + 1) % 5 == _OVR_CHAIN.index(b)


def _score_from_branch_relation(day_oh: OHaeng, branch_oh: OHaeng, w: _DeukWeight) -> int:
    if branch_oh is day_oh:
        return w.bigeop
    if _generates(branch_oh, day_oh):
        return w.inseong
    if _generates(day_oh, branch_oh):
        return w.siksang
    if _overcomes(day_oh, branch_oh):
        return w.jaeseong
    if _overcomes(branch_oh, day_oh):
        return w.gwansal
    return 0


def _score_from_stem_relation(day_oh: OHaeng, stem_oh: OHaeng) -> int:
    if stem_oh is day_oh:
        return 5  # 비견
    if _generates(stem_oh, day_oh):
        return 5  # 인성
    if _overcomes(stem_oh, day_oh):
        return -5  # 관살
    if _overcomes(day_oh, stem_oh):
        return -5  # 재성
    return 0  # 식상


def _level_of(total: int) -> IlganStrengthLevel:
    if total >= 80:
        return IlganStrengthLevel.GEUKSINKANG
    if total >= 65:
        return IlganStrengthLevel.SINKANG
    if total >= 40:
        return IlganStrengthLevel.JUNGHWA
    if total >= 25:
        return IlganStrengthLevel.SINYAK
    return IlganStrengthLevel.GEUKSINYAK


class IlganStrengthAnalyzer:
    """일간 강약 분석기."""

    @staticmethod
    def analyze(saju: Saju) -> IlganStrengthBreakdown:
        day_oh = saju.day_stem.o_haeng

        # 득령: 월지
        deuk_ryeong = _score_from_branch_relation(
            day_oh, saju.month_pillar.ji_ji.o_haeng, _MONTH_BRANCH_W
        )
        # 득지: 일지
        deuk_ji = _score_from_branch_relation(
            day_oh, saju.day_pillar.ji_ji.o_haeng, _DAY_BRANCH_W
        )

        # 득세: 연지 + 시지 + 천간(일간 외)
        deuk_sae = 0
        deuk_sae += _score_from_branch_relation(
            day_oh, saju.year_pillar.ji_ji.o_haeng, _OTHER_BRANCH_W
        )
        if saju.hour_pillar is not None:
            deuk_sae += _score_from_branch_relation(
                day_oh, saju.hour_pillar.ji_ji.o_haeng, _OTHER_BRANCH_W
            )

        other_stems: list[CheonGan] = [saju.year_pillar.cheon_gan, saju.month_pillar.cheon_gan]
        if saju.hour_pillar is not None:
            other_stems.append(saju.hour_pillar.cheon_gan)

        all_branches: list[JiJi] = [
            saju.year_pillar.ji_ji,
            saju.month_pillar.ji_ji,
            saju.day_pillar.ji_ji,
        ]
        if saju.hour_pillar is not None:
            all_branches.append(saju.hour_pillar.ji_ji)

        for stem in other_stems:
            raw = _score_from_stem_relation(day_oh, stem.o_haeng)
            if raw > 0:
                # 비겁/인성 → 뿌리(根) 검사. 본기/중기에만 인정.
                has_root = False
                for b in all_branches:
                    if b.o_haeng is stem.o_haeng:
                        has_root = True
                        break
                    if any(
                        j.stem.o_haeng is stem.o_haeng and j.role is not JiJangGanRole.YEOGI
                        for j in b.ji_jang_gan
                    ):
                        has_root = True
                        break
                deuk_sae += raw if has_root else round(raw / 2.5)
            else:
                deuk_sae += raw

        # 합충형파해
        haps = HapChungAnalyzer.detect_hap(saju)
        chungs = HapChungAnalyzer.detect_chung_hyung(saju)
        hap_chung_adjust = HapChungAnalyzer.strength_adjustment(
            saju=saju, haps=haps, chung_hyungs=chungs
        )

        raw_total = deuk_ryeong + deuk_ji + deuk_sae + hap_chung_adjust
        total = max(0, min(100, 50 + raw_total))
        level = _level_of(total)
        reason = (
            f"득령(월지 {saju.month_pillar.ji_ji.hangul}) {deuk_ryeong}점 / "
            f"득지(일지 {saju.day_pillar.ji_ji.hangul}) {deuk_ji}점 / "
            f"득세 {deuk_sae}점 / 합충형파해 {hap_chung_adjust}점"
        )
        return IlganStrengthBreakdown(
            deuk_ryeong=deuk_ryeong,
            deuk_ji=deuk_ji,
            deuk_sae=deuk_sae,
            hap_chung_adjust=hap_chung_adjust,
            total=total,
            level=level,
            reason=reason,
        )
