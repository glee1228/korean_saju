"""합충형파해(合沖刑破害) — 4기둥 천간/지지 간 관계 검출."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .cheon_gan import CheonGan
from .ji_ji import JiJi
from .o_haeng import OHaeng
from .saju import Saju


class HapKind(Enum):
    CHEON_GAN_HAP = ("天干合", "천간합")
    YUK_HAP = ("六合", "육합")
    SAM_HAP = ("三合", "삼합")
    BAN_HAP = ("半合", "반합")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul


class ChungHyungKind(Enum):
    CHUNG = ("沖", "충")
    HYUNG = ("刑", "형")
    PA = ("破", "파")
    HAE = ("害", "해")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul


@dataclass(frozen=True, slots=True)
class HapDetection:
    kind: HapKind
    members: str
    hwa_o_haeng: OHaeng | None = None

    def __str__(self) -> str:
        hwa = f"→{self.hwa_o_haeng.hangul}" if self.hwa_o_haeng is not None else ""
        return f"{self.kind.hangul}({self.members}{hwa})"


@dataclass(frozen=True, slots=True)
class ChungHyungDetection:
    kind: ChungHyungKind
    members: str

    def __str__(self) -> str:
        return f"{self.kind.hangul}({self.members})"


@dataclass(frozen=True, slots=True)
class _CheonGanHapSpec:
    pair: tuple[CheonGan, CheonGan]
    hwa: OHaeng


@dataclass(frozen=True, slots=True)
class _SamHapSpec:
    triple: tuple[JiJi, JiJi, JiJi]
    hwa: OHaeng


@dataclass(frozen=True, slots=True)
class _YukHapSpec:
    pair: tuple[JiJi, JiJi]
    hwa: OHaeng


_CHEON_GAN_HAPS: tuple[_CheonGanHapSpec, ...] = (
    _CheonGanHapSpec((CheonGan.GAP, CheonGan.GI), OHaeng.TO),
    _CheonGanHapSpec((CheonGan.EUL, CheonGan.GYEONG), OHaeng.GEUM),
    _CheonGanHapSpec((CheonGan.BYEONG, CheonGan.SIN), OHaeng.SU),
    _CheonGanHapSpec((CheonGan.JEONG, CheonGan.IM), OHaeng.MOK),
    _CheonGanHapSpec((CheonGan.MU, CheonGan.GYE), OHaeng.HWA),
)

_SAM_HAPS: tuple[_SamHapSpec, ...] = (
    _SamHapSpec((JiJi.SIN, JiJi.JA, JiJi.JIN), OHaeng.SU),
    _SamHapSpec((JiJi.IN, JiJi.O, JiJi.SUL), OHaeng.HWA),
    _SamHapSpec((JiJi.SA, JiJi.YU, JiJi.CHUK), OHaeng.GEUM),
    _SamHapSpec((JiJi.HAE, JiJi.MYO, JiJi.MI), OHaeng.MOK),
)

_YUK_HAPS: tuple[_YukHapSpec, ...] = (
    _YukHapSpec((JiJi.JA, JiJi.CHUK), OHaeng.TO),
    _YukHapSpec((JiJi.IN, JiJi.HAE), OHaeng.MOK),
    _YukHapSpec((JiJi.MYO, JiJi.SUL), OHaeng.HWA),
    _YukHapSpec((JiJi.JIN, JiJi.YU), OHaeng.GEUM),
    _YukHapSpec((JiJi.SA, JiJi.SIN), OHaeng.SU),
    _YukHapSpec((JiJi.O, JiJi.MI), OHaeng.HWA),
)

_CHUNGS: tuple[tuple[JiJi, JiJi], ...] = (
    (JiJi.JA, JiJi.O),
    (JiJi.CHUK, JiJi.MI),
    (JiJi.IN, JiJi.SIN),
    (JiJi.MYO, JiJi.YU),
    (JiJi.JIN, JiJi.SUL),
    (JiJi.SA, JiJi.HAE),
)

_SAM_HYUNGS: tuple[tuple[JiJi, JiJi, JiJi], ...] = (
    (JiJi.IN, JiJi.SA, JiJi.SIN),  # 持勢之刑
    (JiJi.CHUK, JiJi.SUL, JiJi.MI),  # 無恩之刑
)

_PAS: tuple[tuple[JiJi, JiJi], ...] = (
    (JiJi.JA, JiJi.YU),
    (JiJi.O, JiJi.MYO),
    (JiJi.SA, JiJi.SIN),
    (JiJi.IN, JiJi.HAE),
    (JiJi.JIN, JiJi.CHUK),
    (JiJi.SUL, JiJi.MI),
)

_HAES: tuple[tuple[JiJi, JiJi], ...] = (
    (JiJi.JA, JiJi.MI),
    (JiJi.CHUK, JiJi.O),
    (JiJi.IN, JiJi.SA),
    (JiJi.MYO, JiJi.JIN),
    (JiJi.SIN, JiJi.HAE),
    (JiJi.YU, JiJi.SUL),
)

_GENERATION_CHAIN = (OHaeng.MOK, OHaeng.HWA, OHaeng.TO, OHaeng.GEUM, OHaeng.SU)


def _generates(a: OHaeng, b: OHaeng) -> bool:
    return (_GENERATION_CHAIN.index(a) + 1) % 5 == _GENERATION_CHAIN.index(b)


def _stems(s: Saju) -> list[CheonGan]:
    result = [s.year_pillar.cheon_gan, s.month_pillar.cheon_gan, s.day_pillar.cheon_gan]
    if s.hour_pillar is not None:
        result.append(s.hour_pillar.cheon_gan)
    return result


def _branches(s: Saju) -> list[JiJi]:
    result = [s.year_pillar.ji_ji, s.month_pillar.ji_ji, s.day_pillar.ji_ji]
    if s.hour_pillar is not None:
        result.append(s.hour_pillar.ji_ji)
    return result


class HapChungAnalyzer:
    """합·충·형·파·해 검출 + 일간 강약 보정."""

    @staticmethod
    def detect_hap(saju: Saju) -> list[HapDetection]:
        result: list[HapDetection] = []
        stems = _stems(saju)
        branches = _branches(saju)

        # 천간합
        for hap in _CHEON_GAN_HAPS:
            if all(s in stems for s in hap.pair):
                result.append(HapDetection(
                    kind=HapKind.CHEON_GAN_HAP,
                    members="".join(s.hanja for s in hap.pair),
                    hwa_o_haeng=hap.hwa,
                ))

        # 지지 삼합
        for sam in _SAM_HAPS:
            if all(b in branches for b in sam.triple):
                result.append(HapDetection(
                    kind=HapKind.SAM_HAP,
                    members="".join(b.hanja for b in sam.triple),
                    hwa_o_haeng=sam.hwa,
                ))

        # 지지 반합 (삼합 중 2개)
        for sam in _SAM_HAPS:
            if all(b in branches for b in sam.triple):
                continue
            for i in range(3):
                for j in range(i + 1, 3):
                    if sam.triple[i] in branches and sam.triple[j] in branches:
                        result.append(HapDetection(
                            kind=HapKind.BAN_HAP,
                            members=f"{sam.triple[i].hanja}{sam.triple[j].hanja}",
                            hwa_o_haeng=sam.hwa,
                        ))

        # 지지 육합
        for yh in _YUK_HAPS:
            if all(b in branches for b in yh.pair):
                result.append(HapDetection(
                    kind=HapKind.YUK_HAP,
                    members="".join(b.hanja for b in yh.pair),
                    hwa_o_haeng=yh.hwa,
                ))

        return result

    @staticmethod
    def detect_chung_hyung(saju: Saju) -> list[ChungHyungDetection]:
        result: list[ChungHyungDetection] = []
        branches = _branches(saju)

        for ch in _CHUNGS:
            if all(b in branches for b in ch):
                result.append(ChungHyungDetection(
                    kind=ChungHyungKind.CHUNG,
                    members="".join(b.hanja for b in ch),
                ))
        for hy in _SAM_HYUNGS:
            if all(b in branches for b in hy):
                result.append(ChungHyungDetection(
                    kind=ChungHyungKind.HYUNG,
                    members="".join(b.hanja for b in hy),
                ))
        # 子卯 형
        if JiJi.JA in branches and JiJi.MYO in branches:
            result.append(ChungHyungDetection(kind=ChungHyungKind.HYUNG, members="子卯"))
        # 자형 (같은 지지 2개 이상)
        for self_branch in (JiJi.JIN, JiJi.O, JiJi.YU, JiJi.HAE):
            if sum(1 for b in branches if b is self_branch) >= 2:
                result.append(ChungHyungDetection(
                    kind=ChungHyungKind.HYUNG,
                    members=f"{self_branch.hanja}{self_branch.hanja}",
                ))
        for pa in _PAS:
            if all(b in branches for b in pa):
                result.append(ChungHyungDetection(
                    kind=ChungHyungKind.PA,
                    members="".join(b.hanja for b in pa),
                ))
        for hae in _HAES:
            if all(b in branches for b in hae):
                result.append(ChungHyungDetection(
                    kind=ChungHyungKind.HAE,
                    members="".join(b.hanja for b in hae),
                ))
        return result

    @staticmethod
    def strength_adjustment(
        *,
        saju: Saju,
        haps: list[HapDetection],
        chung_hyungs: list[ChungHyungDetection],
    ) -> int:
        """합화 보정 + 충형파해 감점 점수 (양수=강화, 음수=약화)."""
        day_oh = saju.day_stem.o_haeng
        adjustment = 0

        for h in haps:
            if h.hwa_o_haeng is None:
                continue
            is_inbi = h.hwa_o_haeng is day_oh or _generates(h.hwa_o_haeng, day_oh)
            bonus = {
                HapKind.SAM_HAP: 12,
                HapKind.BAN_HAP: 6,
                HapKind.YUK_HAP: 3,
                HapKind.CHEON_GAN_HAP: 8,
            }[h.kind]
            adjustment += bonus if is_inbi else -(bonus // 2)

        for c in chung_hyungs:
            adjustment -= {
                ChungHyungKind.CHUNG: 10,
                ChungHyungKind.HYUNG: 6,
                ChungHyungKind.PA: 3,
                ChungHyungKind.HAE: 3,
            }[c.kind]
        return adjustment
