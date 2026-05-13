"""격국(格局) — 자평진전 표준 8정격 + 건록격·양인격."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cheon_gan import CheonGan
from .ji_jang_gan import JiJangGanComponent, JiJangGanRole
from .ji_ji import JiJi
from .saju import Saju
from .shipsin import Shipsin, ShipsinCalculator


class Gyeokguk(Enum):
    SIKSIN_GYEOK = ("食神格", "식신격")
    SANGGWAN_GYEOK = ("傷官格", "상관격")
    PYEONJAE_GYEOK = ("偏財格", "편재격")
    JEONGJAE_GYEOK = ("正財格", "정재격")
    PYEONGWAN_GYEOK = ("偏官格", "편관격")
    JEONGGWAN_GYEOK = ("正官格", "정관격")
    PYEONIN_GYEOK = ("偏印格", "편인격")
    JEONGIN_GYEOK = ("正印格", "정인격")
    GEON_ROK_GYEOK = ("建祿格", "건록격")
    YANG_IN_GYEOK = ("羊刃格", "양인격")

    def __init__(self, hanja: str, hangul: str) -> None:
        self.hanja = hanja
        self.hangul = hangul

    @classmethod
    def from_shipsin(cls, s: Shipsin) -> Gyeokguk:
        return _SHIPSIN_TO_GYEOKGUK[s]


_SHIPSIN_TO_GYEOKGUK: dict[Shipsin, Gyeokguk] = {
    Shipsin.BIGYEON: Gyeokguk.GEON_ROK_GYEOK,
    Shipsin.GEOPJAE: Gyeokguk.YANG_IN_GYEOK,
    Shipsin.SIKSIN: Gyeokguk.SIKSIN_GYEOK,
    Shipsin.SANGGWAN: Gyeokguk.SANGGWAN_GYEOK,
    Shipsin.PYEONJAE: Gyeokguk.PYEONJAE_GYEOK,
    Shipsin.JEONGJAE: Gyeokguk.JEONGJAE_GYEOK,
    Shipsin.PYEONGWAN: Gyeokguk.PYEONGWAN_GYEOK,
    Shipsin.JEONGGWAN: Gyeokguk.JEONGGWAN_GYEOK,
    Shipsin.PYEONIN: Gyeokguk.PYEONIN_GYEOK,
    Shipsin.JEONGIN: Gyeokguk.JEONGIN_GYEOK,
}

_ROK_POSITION: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.IN, CheonGan.EUL: JiJi.MYO,
    CheonGan.BYEONG: JiJi.SA, CheonGan.JEONG: JiJi.O,
    CheonGan.MU: JiJi.SA, CheonGan.GI: JiJi.O,
    CheonGan.GYEONG: JiJi.SIN, CheonGan.SIN: JiJi.YU,
    CheonGan.IM: JiJi.HAE, CheonGan.GYE: JiJi.JA,
}

# 양일간: 12운성 제왕 (록의 다음). 음일간: 12운성 관대 (한국 유파 — 진기 논리).
_YANG_IN_POSITION: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.MYO, CheonGan.BYEONG: JiJi.O,
    CheonGan.MU: JiJi.O, CheonGan.GYEONG: JiJi.YU, CheonGan.IM: JiJi.JA,
    CheonGan.EUL: JiJi.JIN, CheonGan.JEONG: JiJi.MI,
    CheonGan.GI: JiJi.MI, CheonGan.SIN: JiJi.SUL, CheonGan.GYE: JiJi.CHUK,
}


@dataclass(frozen=True, slots=True)
class GyeokgukResult:
    gyeokguk: Gyeokguk
    basis_stem: CheonGan
    basis: str

    def __str__(self) -> str:
        return f"{self.gyeokguk.hangul}({self.gyeokguk.hanja}) — {self.basis}"


def _stems_in(saju: Saju) -> set[CheonGan]:
    result = {saju.year_pillar.cheon_gan, saju.month_pillar.cheon_gan}
    if saju.hour_pillar is not None:
        result.add(saju.hour_pillar.cheon_gan)
    return result


def _bongi_first_order(components: list[JiJangGanComponent]) -> list[JiJangGanComponent]:
    bongi = next(c for c in components if c.role is JiJangGanRole.BONGI)
    junggi = [c for c in components if c.role is JiJangGanRole.JUNGGI]
    yeogi = [c for c in components if c.role is JiJangGanRole.YEOGI]
    return [bongi, *junggi, *yeogi]


class GyeokgukCalculator:
    """격국 결정."""

    @staticmethod
    def determine(saju: Saju) -> GyeokgukResult:
        month_branch = saju.month_pillar.ji_ji
        day_stem = saju.day_stem

        # 0. 월지가 일간 록 위치 → 건록격
        if _ROK_POSITION[day_stem] is month_branch:
            return GyeokgukResult(
                gyeokguk=Gyeokguk.GEON_ROK_GYEOK,
                basis_stem=day_stem,
                basis=f"월지 {month_branch.hangul}이 일간 {day_stem.hangul}의 록(祿) 위치",
            )

        # 1. 월지가 일간 양인 위치 → 양인격
        if _YANG_IN_POSITION[day_stem] is month_branch:
            label = "제왕" if day_stem.is_yang else "관대 — 진기 논리"
            return GyeokgukResult(
                gyeokguk=Gyeokguk.YANG_IN_GYEOK,
                basis_stem=day_stem,
                basis=f"월지 {month_branch.hangul}이 일간 {day_stem.hangul}의 양인({label}) 위치",
            )

        # 2. 8정격 — 월지 본기→중기→여기 투간 검사 (일간 제외)
        stems_in_saju = _stems_in(saju)
        for component in _bongi_first_order(month_branch.ji_jang_gan):
            if component.stem in stems_in_saju:
                shipsin = ShipsinCalculator.for_cheon_gan(day_stem, component.stem)
                if shipsin in (Shipsin.BIGYEON, Shipsin.GEOPJAE):
                    continue
                return GyeokgukResult(
                    gyeokguk=Gyeokguk.from_shipsin(shipsin),
                    basis_stem=component.stem,
                    basis=f"월지 {component.role.hangul} 투간",
                )

        # 3. fallback — 월지 본기 십신
        bongi = month_branch.bongi
        shipsin = ShipsinCalculator.for_cheon_gan(day_stem, bongi)
        return GyeokgukResult(
            gyeokguk=Gyeokguk.from_shipsin(shipsin),
            basis_stem=bongi,
            basis="월지 본기 (투간 없음)",
        )
