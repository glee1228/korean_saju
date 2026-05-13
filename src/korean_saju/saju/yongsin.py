"""용신(用神) 도출 — 자평 표준. 외격 → 억부 → 조후 흐름."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ilgan_strength import IlganStrengthAnalyzer, IlganStrengthBreakdown, IlganStrengthLevel
from .johu import JohuAnalysis, JohuAnalyzer
from .o_haeng import OHaeng
from .oegyeok import OegyeokResult, OegyeokType, OegyeokVerdict
from .saju import Saju


class YongsinRole(Enum):
    YONG = ("用神", "용신", "사주를 가장 좋게 하는 오행")
    HEE = ("喜神", "희신", "용신을 보좌·생조하는 오행")
    HAN = ("閑神", "한신", "중립 — 길흉 약함")
    GU = ("仇神", "구신", "기신을 도와주는 오행")
    GI = ("忌神", "기신", "용신을 극하는 오행 — 가장 흉")

    def __init__(self, hanja: str, hangul: str, description: str) -> None:
        self.hanja = hanja
        self.hangul = hangul
        self.description = description


class YongsinMethod(Enum):
    JEONWANG = ("全旺", "전왕")
    EOKBU = ("抑扶", "억부")
    JOHU = ("調候", "조후")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul


@dataclass(frozen=True, slots=True)
class YongsinResult:
    yong_o_haeng: OHaeng
    method: YongsinMethod
    classifications: dict[OHaeng, YongsinRole]
    reason: str
    bo_o_haeng: OHaeng | None = None
    bo_method: YongsinMethod | None = None
    ilgan_strength: IlganStrengthBreakdown | None = None
    johu: JohuAnalysis | None = None

    def role_for(self, o: OHaeng) -> YongsinRole:
        return self.classifications[o]

    @property
    def has_bo_o_haeng(self) -> bool:
        return self.bo_o_haeng is not None

    def __str__(self) -> str:
        base = f"용신={self.yong_o_haeng.hangul}[{self.method.hangul}]"
        if self.has_bo_o_haeng and self.bo_method is not None:
            return f"{base} / 보조={self.bo_o_haeng.hangul}[{self.bo_method.hangul}]"  # type: ignore[union-attr]
        return base


_GEN_CHAIN = (OHaeng.MOK, OHaeng.HWA, OHaeng.TO, OHaeng.GEUM, OHaeng.SU)
_OVR_CHAIN = (OHaeng.MOK, OHaeng.TO, OHaeng.SU, OHaeng.HWA, OHaeng.GEUM)


def _generated_by(o: OHaeng) -> OHaeng:
    return _GEN_CHAIN[(_GEN_CHAIN.index(o) + 1) % 5]


def _generating_of(o: OHaeng) -> OHaeng:
    return _GEN_CHAIN[(_GEN_CHAIN.index(o) - 1 + 5) % 5]


def _overcoming_of(o: OHaeng) -> OHaeng:
    return _OVR_CHAIN[(_OVR_CHAIN.index(o) + 1) % 5]


def _overcoming_from(o: OHaeng) -> OHaeng:
    return _OVR_CHAIN[(_OVR_CHAIN.index(o) - 1 + 5) % 5]


def _classify(yong: OHaeng) -> dict[OHaeng, YongsinRole]:
    hee = _generating_of(yong)
    gi = _overcoming_from(yong)
    gu = _generating_of(gi)
    assigned = {yong, hee, gi, gu}
    han = next(o for o in OHaeng if o not in assigned)
    return {
        yong: YongsinRole.YONG,
        hee: YongsinRole.HEE,
        gi: YongsinRole.GI,
        gu: YongsinRole.GU,
        han: YongsinRole.HAN,
    }


def _eokbu_yongsin(day_oh: OHaeng, level: IlganStrengthLevel) -> OHaeng:
    """일간 강약 등급 → 억부 용신."""
    if level is IlganStrengthLevel.GEUKSINKANG:
        return _overcoming_from(day_oh)  # 관살
    if level is IlganStrengthLevel.SINKANG:
        return _generated_by(day_oh)  # 식상
    if level is IlganStrengthLevel.JUNGHWA:
        return _generated_by(day_oh)  # 식상
    if level is IlganStrengthLevel.SINYAK:
        return _generating_of(day_oh)  # 인성
    return day_oh  # 극신약 → 비겁


def _core_o_haeng_of_oegyeok(type_: OegyeokType, day_oh: OHaeng) -> OHaeng:
    mapping: dict[OegyeokType, OHaeng] = {
        OegyeokType.HWA_GI_GAP_GI_TO: OHaeng.TO,
        OegyeokType.HWA_GI_EUL_GYEONG_GEUM: OHaeng.GEUM,
        OegyeokType.HWA_GI_BYEONG_SIN_SU: OHaeng.SU,
        OegyeokType.HWA_GI_JEONG_IM_MOK: OHaeng.MOK,
        OegyeokType.HWA_GI_MU_GYE_HWA: OHaeng.HWA,
        OegyeokType.GOK_JIK: OHaeng.MOK,
        OegyeokType.YEOM_SANG: OHaeng.HWA,
        OegyeokType.GA_SAEK: OHaeng.TO,
        OegyeokType.JONG_HYEOK: OHaeng.GEUM,
        OegyeokType.YUN_HA: OHaeng.SU,
    }
    if type_ in mapping:
        return mapping[type_]
    if type_ in (OegyeokType.JONG_WANG, OegyeokType.JONG_GANG, OegyeokType.YANG_SIN_SEONG_SANG):
        return day_oh
    if type_ is OegyeokType.JONG_JAE:
        return _overcoming_of(day_oh)
    if type_ is OegyeokType.JONG_GWAN_SAL:
        return _overcoming_from(day_oh)
    if type_ is OegyeokType.JONG_A:
        return _generated_by(day_oh)
    raise ValueError(f"unknown OegyeokType: {type_}")


class YongsinDeriver:
    """용신 도출."""

    @staticmethod
    def derive(saju: Saju, oegyeok_accepted: list[OegyeokResult]) -> YongsinResult:
        day_oh = saju.day_stem.o_haeng

        # 1. 외격 진격 → 전왕
        genuine = [r for r in oegyeok_accepted if r.verdict is OegyeokVerdict.GENUINE]
        if genuine:
            type_ = genuine[0].type
            core = _core_o_haeng_of_oegyeok(type_, day_oh)
            return YongsinResult(
                yong_o_haeng=core,
                method=YongsinMethod.JEONWANG,
                classifications=_classify(core),
                reason=f"외격 {type_.hangul} 진격 → 종할 오행 {core.hangul}",
            )

        # 2. 일간 강약
        ilgan = IlganStrengthAnalyzer.analyze(saju)
        # 3. 억부 용신
        eokbu = _eokbu_yongsin(day_oh, ilgan.level)
        # 4. 조후 용신
        johu = JohuAnalyzer.analyze(saju)

        # 5. 조후/억부 결정
        if eokbu is johu.required_o_haeng:
            yong = eokbu
            method = YongsinMethod.JOHU
            bo: OHaeng | None = None
            bo_method: YongsinMethod | None = None
            merge_reason = f"조후·억부 일치 ({yong.hangul}). 매우 안정된 용신."
        elif johu.urgency >= 50:
            yong = johu.required_o_haeng
            method = YongsinMethod.JOHU
            bo = eokbu
            bo_method = YongsinMethod.EOKBU
            merge_reason = (
                f"조후 {johu.hanyeol_label} ({johu.urgency}점) → "
                f"조후 {yong.hangul} 주용신, 억부 {bo.hangul} 보조."
            )
        else:
            yong = eokbu
            method = YongsinMethod.EOKBU
            bo = None
            bo_method = None
            merge_reason = (
                f"조후 영향 미약 ({johu.urgency}점) → "
                f"억부 {yong.hangul} 단독. {ilgan.level.hangul}."
            )

        return YongsinResult(
            yong_o_haeng=yong,
            method=method,
            bo_o_haeng=bo,
            bo_method=bo_method,
            classifications=_classify(yong),
            ilgan_strength=ilgan,
            johu=johu,
            reason=f"{ilgan.reason} → {ilgan.level.hangul}. {merge_reason}",
        )
