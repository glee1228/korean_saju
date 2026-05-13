"""십신(十神) — 일간 기준 다른 천간/지지(본기)의 10가지 관계."""

from __future__ import annotations

from enum import Enum

from .cheon_gan import CheonGan
from .ji_ji import JiJi
from .o_haeng import OHaeng


class Shipsin(Enum):
    BIGYEON = ("比肩", "비견", "형제·동료·경쟁자. 같은 오행·같은 음양.")
    GEOPJAE = ("劫財", "겁재", "이복형제·라이벌. 같은 오행·다른 음양.")
    SIKSIN = ("食神", "식신", "표현·재물 창출. 일간이 생함·같은 음양.")
    SANGGWAN = ("傷官", "상관", "자기표현·반항·재능. 일간이 생함·다른 음양.")
    PYEONJAE = ("偏財", "편재", "유동자산·아버지·여자(남). 일간이 극함·같은 음양.")
    JEONGJAE = ("正財", "정재", "안정 재물·정처(남). 일간이 극함·다른 음양.")
    PYEONGWAN = ("偏官", "편관", "권위·압박·도전(=칠살). 일간을 극함·같은 음양.")
    JEONGGWAN = ("正官", "정관", "명예·자녀(여)·남편. 일간을 극함·다른 음양.")
    PYEONIN = ("偏印", "편인", "의외의 도움·계모·재주. 일간을 생함·같은 음양.")
    JEONGIN = ("正印", "정인", "어머니·정통 학문·문서. 일간을 생함·다른 음양.")

    def __init__(self, hanja: str, hangul: str, description: str) -> None:
        self.hanja = hanja
        self.hangul = hangul
        self.description = description


# 오행 상생: 木→火→土→金→水→木
_GENERATION_CHAIN = (OHaeng.MOK, OHaeng.HWA, OHaeng.TO, OHaeng.GEUM, OHaeng.SU)
# 오행 상극: 木→土→水→火→金→木
_OVERCOMING_CHAIN = (OHaeng.MOK, OHaeng.TO, OHaeng.SU, OHaeng.HWA, OHaeng.GEUM)


def _generates(a: OHaeng, b: OHaeng) -> bool:
    ai = _GENERATION_CHAIN.index(a)
    bi = _GENERATION_CHAIN.index(b)
    return (ai + 1) % 5 == bi


def _overcomes(a: OHaeng, b: OHaeng) -> bool:
    ai = _OVERCOMING_CHAIN.index(a)
    bi = _OVERCOMING_CHAIN.index(b)
    return (ai + 1) % 5 == bi


class ShipsinCalculator:
    """일간 기준 십신 계산."""

    @staticmethod
    def for_cheon_gan(day_stem: CheonGan, target: CheonGan) -> Shipsin:
        same_polarity = day_stem.yin_yang is target.yin_yang
        day_oh = day_stem.o_haeng
        target_oh = target.o_haeng

        if day_oh is target_oh:
            return Shipsin.BIGYEON if same_polarity else Shipsin.GEOPJAE
        if _generates(day_oh, target_oh):
            return Shipsin.SIKSIN if same_polarity else Shipsin.SANGGWAN
        if _generates(target_oh, day_oh):
            return Shipsin.PYEONIN if same_polarity else Shipsin.JEONGIN
        if _overcomes(day_oh, target_oh):
            return Shipsin.PYEONJAE if same_polarity else Shipsin.JEONGJAE
        if _overcomes(target_oh, day_oh):
            return Shipsin.PYEONGWAN if same_polarity else Shipsin.JEONGGWAN
        raise RuntimeError(f"unreachable: day_oh={day_oh} target_oh={target_oh}")

    @staticmethod
    def for_ji_ji(day_stem: CheonGan, target: JiJi) -> Shipsin:
        return ShipsinCalculator.for_cheon_gan(day_stem, target.bongi)
