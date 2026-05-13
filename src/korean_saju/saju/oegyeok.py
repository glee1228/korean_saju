"""외격(外格) — Negative-First + Confidence Score 100점제.

화기격 5 + 종격 5 + 일행득기 5 + 양신성상 1 = 16종.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cheon_gan import CheonGan
from .ji_jang_gan import JiJangGanRole
from .ji_ji import JiJi
from .o_haeng import OHaeng
from .saju import Saju
from .shipsin import Shipsin, ShipsinCalculator

# 점수 임계값 (조정 가능)
_SCORE_GENUINE = 90
_SCORE_FAKE = 70
_PENALTY_JIJANGGAN_ROOT = 30
_PENALTY_GASIN = 40
_PENALTY_CHONG_CONFLICT = 50
_PENALTY_POWER_INSUFFICIENT = 30
_PENALTY_OHAENG_STEM = 40
_PENALTY_OHAENG_BRANCH = 30


class OegyeokType(Enum):
    # 화기격 5
    HWA_GI_GAP_GI_TO = ("甲己合化土格", "갑기합화토격")
    HWA_GI_EUL_GYEONG_GEUM = ("乙庚合化金格", "을경합화금격")
    HWA_GI_BYEONG_SIN_SU = ("丙辛合化水格", "병신합화수격")
    HWA_GI_JEONG_IM_MOK = ("丁壬合化木格", "정임합화목격")
    HWA_GI_MU_GYE_HWA = ("戊癸合化火格", "무계합화화격")
    # 종격 5
    JONG_WANG = ("從旺格", "종왕격")
    JONG_GANG = ("從強格", "종강격")
    JONG_JAE = ("從財格", "종재격")
    JONG_GWAN_SAL = ("從官殺格", "종관살격")
    JONG_A = ("從兒格", "종아격")
    # 일행득기 5
    GOK_JIK = ("曲直格", "곡직격")
    YEOM_SANG = ("炎上格", "염상격")
    GA_SAEK = ("稼穡格", "가색격")
    JONG_HYEOK = ("從革格", "종혁격")
    YUN_HA = ("潤下格", "윤하격")
    # 양신성상
    YANG_SIN_SEONG_SANG = ("兩神成象格", "양신성상격")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul


class OegyeokVerdict(Enum):
    GENUINE = "진격(眞格)"
    FAKE = "가격(假格)"
    REJECTED = "정격 사용"

    def __init__(self, label: str) -> None:
        self.label = label


@dataclass(frozen=True, slots=True)
class OegyeokResult:
    type: OegyeokType
    verdict: OegyeokVerdict
    score: int
    reason: str

    @property
    def is_accepted(self) -> bool:
        return self.verdict is not OegyeokVerdict.REJECTED

    def __str__(self) -> str:
        return f"{self.type.hangul} [{self.verdict.label}] {self.score}점 — {self.reason}"


@dataclass(frozen=True, slots=True)
class _HwaGiSpec:
    partner_a: CheonGan
    partner_b: CheonGan
    core_o_haeng: OHaeng


_HWAGI_SPECS: dict[OegyeokType, _HwaGiSpec] = {
    OegyeokType.HWA_GI_GAP_GI_TO: _HwaGiSpec(CheonGan.GAP, CheonGan.GI, OHaeng.TO),
    OegyeokType.HWA_GI_EUL_GYEONG_GEUM: _HwaGiSpec(CheonGan.EUL, CheonGan.GYEONG, OHaeng.GEUM),
    OegyeokType.HWA_GI_BYEONG_SIN_SU: _HwaGiSpec(CheonGan.BYEONG, CheonGan.SIN, OHaeng.SU),
    OegyeokType.HWA_GI_JEONG_IM_MOK: _HwaGiSpec(CheonGan.JEONG, CheonGan.IM, OHaeng.MOK),
    OegyeokType.HWA_GI_MU_GYE_HWA: _HwaGiSpec(CheonGan.MU, CheonGan.GYE, OHaeng.HWA),
}

_ILHAENG_CORE_OHAENG: dict[OegyeokType, OHaeng] = {
    OegyeokType.GOK_JIK: OHaeng.MOK,
    OegyeokType.YEOM_SANG: OHaeng.HWA,
    OegyeokType.GA_SAEK: OHaeng.TO,
    OegyeokType.JONG_HYEOK: OHaeng.GEUM,
    OegyeokType.YUN_HA: OHaeng.SU,
}

_HWAGI_TYPES = frozenset({
    OegyeokType.HWA_GI_GAP_GI_TO, OegyeokType.HWA_GI_EUL_GYEONG_GEUM,
    OegyeokType.HWA_GI_BYEONG_SIN_SU, OegyeokType.HWA_GI_JEONG_IM_MOK,
    OegyeokType.HWA_GI_MU_GYE_HWA,
})
_JONG_TYPES = frozenset({
    OegyeokType.JONG_WANG, OegyeokType.JONG_GANG, OegyeokType.JONG_JAE,
    OegyeokType.JONG_GWAN_SAL, OegyeokType.JONG_A,
})
_ILHAENG_TYPES = frozenset(_ILHAENG_CORE_OHAENG.keys())

_GEN_CHAIN = (OHaeng.MOK, OHaeng.HWA, OHaeng.TO, OHaeng.GEUM, OHaeng.SU)
_OVR_CHAIN = (OHaeng.MOK, OHaeng.TO, OHaeng.SU, OHaeng.HWA, OHaeng.GEUM)


def _generates(a: OHaeng, b: OHaeng) -> bool:
    return (_GEN_CHAIN.index(a) + 1) % 5 == _GEN_CHAIN.index(b)


def _overcomes(a: OHaeng, b: OHaeng) -> bool:
    return (_OVR_CHAIN.index(a) + 1) % 5 == _OVR_CHAIN.index(b)


def _generated_by(o: OHaeng) -> OHaeng:
    return _GEN_CHAIN[(_GEN_CHAIN.index(o) + 1) % 5]


def _generating_of(o: OHaeng) -> OHaeng:
    return _GEN_CHAIN[(_GEN_CHAIN.index(o) - 1 + 5) % 5]


def _overcoming_of(o: OHaeng) -> OHaeng:
    return _OVR_CHAIN[(_OVR_CHAIN.index(o) + 1) % 5]


def _overcoming_from(o: OHaeng) -> OHaeng:
    return _OVR_CHAIN[(_OVR_CHAIN.index(o) - 1 + 5) % 5]


def _all_stems(saju: Saju) -> list[CheonGan]:
    result = [saju.year_pillar.cheon_gan, saju.month_pillar.cheon_gan, saju.day_pillar.cheon_gan]
    if saju.hour_pillar is not None:
        result.append(saju.hour_pillar.cheon_gan)
    return result


def _all_branches(saju: Saju) -> list[JiJi]:
    result = [saju.year_pillar.ji_ji, saju.month_pillar.ji_ji, saju.day_pillar.ji_ji]
    if saju.hour_pillar is not None:
        result.append(saju.hour_pillar.ji_ji)
    return result


def _has_ji_ji_root(stem: CheonGan, saju: Saju) -> bool:
    stem_oh = stem.o_haeng
    for branch in _all_branches(saju):
        if branch.o_haeng is stem_oh:
            return True
        for jjg in branch.ji_jang_gan:
            if jjg.stem.o_haeng is stem_oh:
                return True
    return False


def _has_o_haeng_anywhere(o: OHaeng, saju: Saju) -> bool:
    for stem in _all_stems(saju):
        if stem.o_haeng is o:
            return True
    for branch in _all_branches(saju):
        for jjg in branch.ji_jang_gan:
            if jjg.stem.o_haeng is o:
                return True
    return False


def _power_of_o_haeng(o: OHaeng, saju: Saju) -> float:
    score = 0.0
    total = 0.0
    for stem in _all_stems(saju):
        total += 1.0
        if stem.o_haeng is o:
            score += 1.0
    for branch in _all_branches(saju):
        for jjg in branch.ji_jang_gan:
            weight = {
                JiJangGanRole.BONGI: 2.0,
                JiJangGanRole.JUNGGI: 1.0,
                JiJangGanRole.YEOGI: 0.5,
            }[jjg.role]
            total += weight
            if jjg.stem.o_haeng is o:
                score += weight
    return 0.0 if total == 0 else score / total


def _count_stems(saju: Saju, target: CheonGan) -> int:
    return sum(1 for s in _all_stems(saju) if s is target)


def _count_shipsin(saju: Saju, targets: frozenset[Shipsin]) -> int:
    count = 0
    for stem in _all_stems(saju):
        if stem is saju.day_stem:
            continue
        s = ShipsinCalculator.for_cheon_gan(saju.day_stem, stem)
        if s in targets:
            count += 1
    return count


def _overcomes_or_conflicts(month_branch: JiJi, target: OHaeng) -> bool:
    return _overcomes(month_branch.o_haeng, target)


def _is_month_branch_in_conflict(saju: Saju) -> bool:
    m = saju.month_pillar.ji_ji.index
    for branch in _all_branches(saju):
        if branch is saju.month_pillar.ji_ji:
            continue
        if abs(branch.index - m) == 6:
            return True
    return False


def _month_branch_season_matches(target: OHaeng, month_branch: JiJi) -> bool:
    season = {
        JiJi.IN: OHaeng.MOK, JiJi.MYO: OHaeng.MOK,
        JiJi.SA: OHaeng.HWA, JiJi.O: OHaeng.HWA,
        JiJi.SIN: OHaeng.GEUM, JiJi.YU: OHaeng.GEUM,
        JiJi.HAE: OHaeng.SU, JiJi.JA: OHaeng.SU,
        JiJi.JIN: OHaeng.TO, JiJi.MI: OHaeng.TO,
        JiJi.SUL: OHaeng.TO, JiJi.CHUK: OHaeng.TO,
    }[month_branch]
    return season is target


def _o_haeng_for_shipsin(day_stem: CheonGan, s: Shipsin) -> OHaeng:
    day_oh = day_stem.o_haeng
    if s in (Shipsin.BIGYEON, Shipsin.GEOPJAE):
        return day_oh
    if s in (Shipsin.SIKSIN, Shipsin.SANGGWAN):
        return _generated_by(day_oh)
    if s in (Shipsin.PYEONJAE, Shipsin.JEONGJAE):
        return _overcoming_of(day_oh)
    if s in (Shipsin.PYEONGWAN, Shipsin.JEONGGWAN):
        return _overcoming_from(day_oh)
    if s in (Shipsin.PYEONIN, Shipsin.JEONGIN):
        return _generating_of(day_oh)
    raise ValueError(f"unknown shipsin: {s}")


def _jong_target_shipsin(type_: OegyeokType) -> frozenset[Shipsin]:
    if type_ is OegyeokType.JONG_JAE:
        return frozenset({Shipsin.PYEONJAE, Shipsin.JEONGJAE})
    if type_ is OegyeokType.JONG_GWAN_SAL:
        return frozenset({Shipsin.PYEONGWAN, Shipsin.JEONGGWAN})
    if type_ is OegyeokType.JONG_A:
        return frozenset({Shipsin.SIKSIN, Shipsin.SANGGWAN})
    raise ValueError(f"not a jong type: {type_}")


def _verdict(type_: OegyeokType, score: int, reasons: list[str]) -> OegyeokResult:
    clamped = max(0, min(100, score))
    if clamped >= _SCORE_GENUINE:
        v = OegyeokVerdict.GENUINE
    elif clamped >= _SCORE_FAKE:
        v = OegyeokVerdict.FAKE
    else:
        v = OegyeokVerdict.REJECTED
    return OegyeokResult(type=type_, verdict=v, score=clamped, reason=", ".join(reasons))


def _analyze_hwa_gi(saju: Saju, type_: OegyeokType) -> OegyeokResult:
    spec = _HWAGI_SPECS[type_]
    day_stem = saju.day_stem
    if day_stem not in (spec.partner_a, spec.partner_b):
        return OegyeokResult(
            type=type_, verdict=OegyeokVerdict.REJECTED, score=0,
            reason=f"일간 {day_stem.hangul}는 {type_.hangul}의 합 페어가 아님",
        )
    hapsin = spec.partner_b if day_stem is spec.partner_a else spec.partner_a
    hapsin_positions: list[str] = []
    if saju.month_pillar.cheon_gan is hapsin:
        hapsin_positions.append("월간")
    if saju.hour_pillar is not None and saju.hour_pillar.cheon_gan is hapsin:
        hapsin_positions.append("시간")
    if not hapsin_positions:
        return OegyeokResult(
            type=type_, verdict=OegyeokVerdict.REJECTED, score=0,
            reason=f"합신 {hapsin.hangul}이 월간·시간에 없음",
        )
    if _overcomes_or_conflicts(saju.month_pillar.ji_ji, spec.core_o_haeng):
        return OegyeokResult(
            type=type_, verdict=OegyeokVerdict.REJECTED, score=0,
            reason=f"월지 {saju.month_pillar.ji_ji.hangul}이 합화 오행 {spec.core_o_haeng.hangul}을 충/극",
        )
    score = 100
    reasons = [f"합신 {hapsin.hangul} {'·'.join(hapsin_positions)} 위치"]
    if not _month_branch_season_matches(spec.core_o_haeng, saju.month_pillar.ji_ji):
        score -= _PENALTY_GASIN
        reasons.append(f"월지 {saju.month_pillar.ji_ji.hangul} 계절감 불일치 (-{_PENALTY_GASIN})")
    extra = _count_stems(saju, day_stem) + _count_stems(saju, hapsin) - 2
    if extra > 0:
        score -= _PENALTY_GASIN
        reasons.append(f"쟁합/투합 발생 (-{_PENALTY_GASIN})")
    if _power_of_o_haeng(spec.core_o_haeng, saju) < 0.3:
        score -= _PENALTY_JIJANGGAN_ROOT
        reasons.append(f"합화 오행 {spec.core_o_haeng.hangul} 지지 근 부족 (-{_PENALTY_JIJANGGAN_ROOT})")
    return _verdict(type_, score, reasons)


def _analyze_jong_wang(saju: Saju) -> OegyeokResult:
    day_oh = saju.day_stem.o_haeng
    power = _power_of_o_haeng(day_oh, saju)
    if power < 0.7:
        return OegyeokResult(
            type=OegyeokType.JONG_WANG, verdict=OegyeokVerdict.REJECTED, score=0,
            reason=f"일간 오행 {day_oh.hangul} 세력 {int(power * 100)}% < 70%",
        )
    month_oh = saju.month_pillar.ji_ji.o_haeng
    if month_oh is not day_oh and not _generates(month_oh, day_oh):
        return OegyeokResult(
            type=OegyeokType.JONG_WANG, verdict=OegyeokVerdict.REJECTED, score=0,
            reason="월지가 일간 오행 또는 인성 오행이 아님",
        )
    score = 100
    reasons = [f"일간 오행 {day_oh.hangul} 세력 {int(power * 100)}%"]
    sik_jae_gwan = _count_shipsin(saju, frozenset({
        Shipsin.SIKSIN, Shipsin.SANGGWAN, Shipsin.PYEONJAE,
        Shipsin.JEONGJAE, Shipsin.PYEONGWAN, Shipsin.JEONGGWAN,
    }))
    if sik_jae_gwan > 0:
        penalty = _PENALTY_GASIN * sik_jae_gwan
        score -= penalty
        reasons.append(f"식재관 천간 {sik_jae_gwan}개 방해 (-{penalty})")
    return _verdict(OegyeokType.JONG_WANG, score, reasons)


def _analyze_jong_gang(saju: Saju) -> OegyeokResult:
    inseong_oh = _o_haeng_for_shipsin(saju.day_stem, Shipsin.JEONGIN)
    power = _power_of_o_haeng(inseong_oh, saju) + _power_of_o_haeng(saju.day_stem.o_haeng, saju)
    if power < 0.8:
        return OegyeokResult(
            type=OegyeokType.JONG_GANG, verdict=OegyeokVerdict.REJECTED, score=0,
            reason=f"인성+비겁 세력 {int(power * 100)}% < 80%",
        )
    score = 100
    reasons = [f"인성+비겁 세력 {int(power * 100)}%"]
    sik_jae_gwan = _count_shipsin(saju, frozenset({
        Shipsin.SIKSIN, Shipsin.SANGGWAN, Shipsin.PYEONJAE,
        Shipsin.JEONGJAE, Shipsin.PYEONGWAN, Shipsin.JEONGGWAN,
    }))
    if sik_jae_gwan > 0:
        penalty = _PENALTY_GASIN * sik_jae_gwan
        score -= penalty
        reasons.append(f"식재관 천간 {sik_jae_gwan}개 방해 (-{penalty})")
    return _verdict(OegyeokType.JONG_GANG, score, reasons)


def _analyze_jong(saju: Saju, type_: OegyeokType) -> OegyeokResult:
    if type_ is OegyeokType.JONG_WANG:
        return _analyze_jong_wang(saju)
    if type_ is OegyeokType.JONG_GANG:
        return _analyze_jong_gang(saju)
    target_shipsin = _jong_target_shipsin(type_)
    target_oh = _o_haeng_for_shipsin(saju.day_stem, next(iter(target_shipsin)))

    if _has_ji_ji_root(saju.day_stem, saju):
        return OegyeokResult(
            type=type_, verdict=OegyeokVerdict.REJECTED, score=0,
            reason=f"일간 {saju.day_stem.hangul}의 근이 지지에 존재 → 종격 불가",
        )
    if _overcomes_or_conflicts(saju.month_pillar.ji_ji, target_oh):
        return OegyeokResult(
            type=type_, verdict=OegyeokVerdict.REJECTED, score=0,
            reason=f"월지 {saju.month_pillar.ji_ji.hangul}이 종할 오행 {target_oh.hangul}을 충/극",
        )
    score = 100
    reasons = [f"종할 오행 {target_oh.hangul}"]
    inseong_bigeop = _count_shipsin(saju, frozenset({
        Shipsin.BIGYEON, Shipsin.GEOPJAE, Shipsin.PYEONIN, Shipsin.JEONGIN,
    }))
    if inseong_bigeop > 0:
        penalty = _PENALTY_GASIN * inseong_bigeop
        score -= penalty
        reasons.append(f"인성·비겁 천간 {inseong_bigeop}개 가신 투출 (-{penalty})")
    power = _power_of_o_haeng(target_oh, saju)
    if power < 0.8:
        score -= _PENALTY_POWER_INSUFFICIENT
        reasons.append(f"종할 오행 세력 {int(power * 100)}% < 80% (-{_PENALTY_POWER_INSUFFICIENT})")
    if _is_month_branch_in_conflict(saju):
        score -= _PENALTY_CHONG_CONFLICT
        reasons.append(f"월지 충 발생 (-{_PENALTY_CHONG_CONFLICT})")
    return _verdict(type_, score, reasons)


def _analyze_ilhaeng_deukgi(saju: Saju, type_: OegyeokType) -> OegyeokResult:
    core_oh = _ILHAENG_CORE_OHAENG[type_]
    if saju.day_stem.o_haeng is not core_oh:
        return OegyeokResult(
            type=type_, verdict=OegyeokVerdict.REJECTED, score=0,
            reason=f"일간 오행 {saju.day_stem.o_haeng.hangul}이 핵심 {core_oh.hangul}이 아님",
        )
    score = 100
    reasons = [f"핵심 오행 {core_oh.hangul}"]
    diff_stems = sum(1 for s in _all_stems(saju) if s.o_haeng is not core_oh)
    if diff_stems > 0:
        penalty = _PENALTY_OHAENG_STEM * diff_stems
        score -= penalty
        reasons.append(f"다른 오행 천간 {diff_stems}개 (-{penalty})")
    diff_branches = sum(1 for b in _all_branches(saju) if b.o_haeng is not core_oh)
    if diff_branches > 0:
        penalty = _PENALTY_OHAENG_BRANCH * diff_branches
        score -= penalty
        reasons.append(f"다른 오행 지지 {diff_branches}개 (-{penalty})")
    overcoming_oh = _overcoming_from(core_oh)
    if _has_o_haeng_anywhere(overcoming_oh, saju):
        score -= _PENALTY_CHONG_CONFLICT
        reasons.append(f"극하는 오행 {overcoming_oh.hangul} 발견 (-{_PENALTY_CHONG_CONFLICT})")
    return _verdict(type_, score, reasons)


def _analyze_yang_sin_seong_sang(saju: Saju) -> OegyeokResult:
    dist = {o: _power_of_o_haeng(o, saju) for o in OHaeng}
    high_two = [(k, v) for k, v in dist.items() if v >= 0.4]
    zero_others = sum(1 for v in dist.values() if v < 0.05)
    if len(high_two) != 2 or zero_others != 3:
        return OegyeokResult(
            type=OegyeokType.YANG_SIN_SEONG_SANG, verdict=OegyeokVerdict.REJECTED, score=0,
            reason="두 오행 40%+ + 나머지 0% 조건 불충족",
        )
    score = 100 - (10 if high_two[0][1] < 0.45 else 0)
    names = "·".join(k.hangul for k, _ in high_two)
    return _verdict(
        OegyeokType.YANG_SIN_SEONG_SANG, score,
        [f"두 오행 {names} 각 40%+, 나머지 0%"],
    )


class OegyeokAnalyzer:
    """외격 분석기."""

    @staticmethod
    def analyze_all(saju: Saju) -> list[OegyeokResult]:
        return [OegyeokAnalyzer.analyze(saju, t) for t in OegyeokType]

    @staticmethod
    def analyze(saju: Saju, type_: OegyeokType) -> OegyeokResult:
        if type_ in _HWAGI_TYPES:
            return _analyze_hwa_gi(saju, type_)
        if type_ in _JONG_TYPES:
            return _analyze_jong(saju, type_)
        if type_ in _ILHAENG_TYPES:
            return _analyze_ilhaeng_deukgi(saju, type_)
        return _analyze_yang_sin_seong_sang(saju)
