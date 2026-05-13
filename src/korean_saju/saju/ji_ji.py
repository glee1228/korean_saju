"""지지(地支) 12개 — 지장간 포함."""

from __future__ import annotations

from enum import Enum

from .cheon_gan import CheonGan
from .ji_jang_gan import JiJangGanComponent, JiJangGanRole
from .o_haeng import OHaeng
from .yin_yang import YinYang


class JiJi(Enum):
    JA = ("子", "자", YinYang.EUM, OHaeng.SU, "쥐 — 한겨울 깊은 밤의 물. 지혜·은밀함·번식력.")
    CHUK = ("丑", "축", YinYang.EUM, OHaeng.TO, "소 — 한겨울 새벽 흙. 인내·묵묵함·근면.")
    IN = ("寅", "인", YinYang.YANG, OHaeng.MOK, "호랑이 — 이른 봄 큰 나무. 진취·도약·리더십.")
    MYO = ("卯", "묘", YinYang.EUM, OHaeng.MOK, "토끼 — 한봄의 풀. 섬세함·평화·예술감.")
    JIN = ("辰", "진", YinYang.YANG, OHaeng.TO, "용 — 봄 끝의 흙(저수지). 변화·잠재력·신비.")
    SA = ("巳", "사", YinYang.YANG, OHaeng.HWA, "뱀 — 초여름 불. 지혜·직관·이지적.")
    O = ("午", "오", YinYang.EUM, OHaeng.HWA, "말 — 한여름 불. 활동·명예·열정.")
    MI = ("未", "미", YinYang.EUM, OHaeng.TO, "양 — 여름 끝 흙. 따뜻함·정·섬세.")
    SIN = ("申", "신", YinYang.YANG, OHaeng.GEUM, "원숭이 — 초가을 금. 영민함·활동·재치.")
    YU = ("酉", "유", YinYang.EUM, OHaeng.GEUM, "닭 — 한가을 금. 정확·단정·결실.")
    SUL = ("戌", "술", YinYang.YANG, OHaeng.TO, "개 — 가을 끝 흙. 충직·보호·신의.")
    HAE = ("亥", "해", YinYang.YANG, OHaeng.SU, "돼지 — 초겨울 물. 풍요·깊이·여유.")

    def __init__(
        self, hanja: str, hangul: str, yin_yang: YinYang, o_haeng: OHaeng, description: str
    ) -> None:
        self.hanja = hanja
        self.hangul = hangul
        self.yin_yang = yin_yang
        self.o_haeng = o_haeng
        self.description = description

    @property
    def index(self) -> int:
        return list(JiJi).index(self)

    @classmethod
    def by_index(cls, index: int) -> JiJi:
        values = list(cls)
        return values[index % 12]

    @classmethod
    def from_hanja(cls, hanja: str) -> JiJi | None:
        for v in cls:
            if v.hanja == hanja:
                return v
        return None

    @property
    def next(self) -> JiJi:
        return JiJi.by_index(self.index + 1)

    @property
    def is_yang(self) -> bool:
        return self.yin_yang is YinYang.YANG

    @property
    def is_eum(self) -> bool:
        return self.yin_yang is YinYang.EUM

    @property
    def ji_jang_gan(self) -> list[JiJangGanComponent]:
        """지장간 — 여기 → 중기 → 본기 순서."""
        return _JI_JANG_GAN_TABLE[self]

    @property
    def bongi(self) -> CheonGan:
        """본기(本氣) — 지장간 중 주된 천간."""
        for c in self.ji_jang_gan:
            if c.role is JiJangGanRole.BONGI:
                return c.stem
        raise RuntimeError(f"no bongi in jiJangGan of {self}")


_JI_JANG_GAN_TABLE: dict[JiJi, list[JiJangGanComponent]] = {
    JiJi.JA: [
        JiJangGanComponent(CheonGan.IM, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.GYE, JiJangGanRole.BONGI),
    ],
    JiJi.CHUK: [
        JiJangGanComponent(CheonGan.GYE, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.SIN, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.GI, JiJangGanRole.BONGI),
    ],
    JiJi.IN: [
        JiJangGanComponent(CheonGan.MU, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.BYEONG, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.GAP, JiJangGanRole.BONGI),
    ],
    JiJi.MYO: [
        JiJangGanComponent(CheonGan.GAP, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.EUL, JiJangGanRole.BONGI),
    ],
    JiJi.JIN: [
        JiJangGanComponent(CheonGan.EUL, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.GYE, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.MU, JiJangGanRole.BONGI),
    ],
    JiJi.SA: [
        JiJangGanComponent(CheonGan.MU, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.GYEONG, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.BYEONG, JiJangGanRole.BONGI),
    ],
    JiJi.O: [
        JiJangGanComponent(CheonGan.BYEONG, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.GI, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.JEONG, JiJangGanRole.BONGI),
    ],
    JiJi.MI: [
        JiJangGanComponent(CheonGan.JEONG, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.EUL, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.GI, JiJangGanRole.BONGI),
    ],
    JiJi.SIN: [
        JiJangGanComponent(CheonGan.MU, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.IM, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.GYEONG, JiJangGanRole.BONGI),
    ],
    JiJi.YU: [
        JiJangGanComponent(CheonGan.GYEONG, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.SIN, JiJangGanRole.BONGI),
    ],
    JiJi.SUL: [
        JiJangGanComponent(CheonGan.SIN, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.JEONG, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.MU, JiJangGanRole.BONGI),
    ],
    JiJi.HAE: [
        JiJangGanComponent(CheonGan.MU, JiJangGanRole.YEOGI),
        JiJangGanComponent(CheonGan.GAP, JiJangGanRole.JUNGGI),
        JiJangGanComponent(CheonGan.IM, JiJangGanRole.BONGI),
    ],
}
