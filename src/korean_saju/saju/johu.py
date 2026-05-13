"""조후(調候) — 한열(寒熱) 평가. 火·水 두 가지로만 판단."""

from __future__ import annotations

from dataclasses import dataclass

from .cheon_gan import CheonGan
from .hapchung import HapChungAnalyzer, HapKind
from .ji_ji import JiJi
from .o_haeng import OHaeng
from .saju import Saju


@dataclass(frozen=True, slots=True)
class JohuAnalysis:
    required_o_haeng: OHaeng  # 火 또는 水
    hanyeol_score: int  # 음수=한, 양수=열
    urgency: int  # 0~100
    reason: str

    @property
    def is_urgent(self) -> bool:
        return self.urgency >= 70

    @property
    def is_moderate(self) -> bool:
        return 30 <= self.urgency < 70

    @property
    def is_han(self) -> bool:
        return self.hanyeol_score < 0

    @property
    def is_yeol(self) -> bool:
        return self.hanyeol_score > 0

    @property
    def hanyeol_label(self) -> str:
        if self.hanyeol_score <= -3:
            return "한습(寒濕)"
        if self.hanyeol_score <= -1:
            return "한기"
        if self.hanyeol_score == 0:
            return "균형"
        if self.hanyeol_score <= 2:
            return "온기"
        return "조열(燥熱)"

    def __str__(self) -> str:
        return (
            f"{self.hanyeol_label} ({self.hanyeol_score}점) → "
            f"{self.required_o_haeng.hangul} 필요 [절실도 {self.urgency}]"
        )


def _season_score(month_branch: JiJi) -> int:
    return {
        JiJi.IN: 1, JiJi.MYO: 1,        # 春
        JiJi.SA: 3, JiJi.O: 3,           # 夏
        JiJi.SIN: -1, JiJi.YU: -1,       # 秋
        JiJi.HAE: -3, JiJi.JA: -3,       # 冬
        JiJi.JIN: 1,                     # 春末
        JiJi.MI: 2,                      # 夏末
        JiJi.SUL: -1,                    # 秋末
        JiJi.CHUK: -2,                   # 冬末
    }[month_branch]


def _season_label(m: JiJi) -> str:
    return {
        JiJi.IN: "春", JiJi.MYO: "春", JiJi.JIN: "春末",
        JiJi.SA: "夏", JiJi.O: "夏", JiJi.MI: "夏末",
        JiJi.SIN: "秋", JiJi.YU: "秋", JiJi.SUL: "秋末",
        JiJi.HAE: "冬", JiJi.JA: "冬", JiJi.CHUK: "冬末",
    }[m]


def _hap_hanyeol_delta(kind: HapKind, hwa: OHaeng | None) -> int:
    if hwa is None:
        return 0
    base = {
        OHaeng.SU: -3,
        OHaeng.HWA: 3,
        OHaeng.GEUM: -1,
        OHaeng.MOK: 1,
        OHaeng.TO: 0,
    }[hwa]
    return round(base / 2) if kind is HapKind.BAN_HAP else base


def _signed(n: int) -> str:
    return f"+{n}" if n > 0 else f"{n}"


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


def _strong_o_haeng_score(target: OHaeng, saju: Saju) -> int:
    count = 0
    for stem in _stems(saju):
        if stem.o_haeng is target:
            count += 1
    for branch in _branches(saju):
        if branch.o_haeng is target:
            count += 1
    return count


class JohuAnalyzer:
    """조후 분석기."""

    @staticmethod
    def analyze(saju: Saju) -> JohuAnalysis:
        reasons: list[str] = []
        hanyeol = 0

        # 1. 월지 계절감
        month_branch = saju.month_pillar.ji_ji
        season_score = _season_score(month_branch)
        hanyeol += season_score
        reasons.append(
            f"월지 {month_branch.hangul}({_season_label(month_branch)}) {_signed(season_score)}"
        )

        # 2. 지지 합·국 보정
        haps = HapChungAnalyzer.detect_hap(saju)
        for h in haps:
            if h.kind not in (HapKind.SAM_HAP, HapKind.BAN_HAP):
                continue
            delta = _hap_hanyeol_delta(h.kind, h.hwa_o_haeng)
            if delta == 0:
                continue
            hanyeol += delta
            hwa_label = h.hwa_o_haeng.hangul if h.hwa_o_haeng is not None else "?"
            reasons.append(
                f"{h.kind.hangul} {h.members}({hwa_label}국) {_signed(delta)}"
            )

        # 3. 火·水 분포 보정
        fire_score = _strong_o_haeng_score(OHaeng.HWA, saju)
        water_score = _strong_o_haeng_score(OHaeng.SU, saju)
        dist_score = fire_score - water_score
        if dist_score != 0:
            hanyeol += dist_score
            reasons.append(f"火 +{fire_score} / 水 -{water_score} ({_signed(dist_score)})")

        # 4. 조후 결정
        if hanyeol <= -3:
            required = OHaeng.HWA
            urgency = max(70, min(100, 90 + (-hanyeol - 3) * 3))
        elif hanyeol <= -1:
            required = OHaeng.HWA
            urgency = 50 + (-hanyeol) * 10
        elif hanyeol == 0:
            required = OHaeng.HWA
            urgency = 20
        elif hanyeol <= 2:
            required = OHaeng.SU
            urgency = 50 + hanyeol * 10
        else:
            required = OHaeng.SU
            urgency = max(70, min(100, 90 + (hanyeol - 3) * 3))

        return JohuAnalysis(
            required_o_haeng=required,
            hanyeol_score=hanyeol,
            urgency=urgency,
            reason=f"{', '.join(reasons)} → {required.hangul} 필요",
        )
