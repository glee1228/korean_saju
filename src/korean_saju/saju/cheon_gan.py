"""천간(天干) 10개."""

from __future__ import annotations

from enum import Enum

from .o_haeng import OHaeng
from .yin_yang import YinYang


class CheonGan(Enum):
    GAP = ("甲", "갑", YinYang.YANG, OHaeng.MOK,
           "큰 나무·소나무 — 진취적이고 시작을 즐기며 우두머리 기질이 있습니다.")
    EUL = ("乙", "을", YinYang.EUM, OHaeng.MOK,
           "풀·꽃·덩굴 — 부드럽고 적응력 강하며 인내가 큽니다.")
    BYEONG = ("丙", "병", YinYang.YANG, OHaeng.HWA,
              "태양 — 밝고 적극적이며 표현과 명예를 추구합니다.")
    JEONG = ("丁", "정", YinYang.EUM, OHaeng.HWA,
             "촛불·등불 — 따뜻하고 섬세하며 지혜로운 빛이 있습니다.")
    MU = ("戊", "무", YinYang.YANG, OHaeng.TO,
          "큰 산·대지 — 든든하고 신뢰감 있으며 묵직합니다.")
    GI = ("己", "기", YinYang.EUM, OHaeng.TO,
          "정원·논밭 — 포용력 있고 기르는 성품, 차분하고 실용적입니다.")
    GYEONG = ("庚", "경", YinYang.YANG, OHaeng.GEUM,
              "무쇠·도끼 — 강직하고 결단력 있으며 의리를 중시합니다.")
    SIN = ("辛", "신", YinYang.EUM, OHaeng.GEUM,
           "보석·세공된 금 — 섬세하고 예리하며 분석력이 뛰어납니다.")
    IM = ("壬", "임", YinYang.YANG, OHaeng.SU,
          "큰 강·바다 — 지혜롭고 유연하며 그릇이 큽니다.")
    GYE = ("癸", "계", YinYang.EUM, OHaeng.SU,
           "비·이슬 — 맑고 섬세하며 직관과 감수성이 뛰어납니다.")

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
        return list(CheonGan).index(self)

    @classmethod
    def by_index(cls, index: int) -> CheonGan:
        values = list(cls)
        return values[index % 10]

    @classmethod
    def from_hanja(cls, hanja: str) -> CheonGan | None:
        for v in cls:
            if v.hanja == hanja:
                return v
        return None

    @property
    def next(self) -> CheonGan:
        return CheonGan.by_index(self.index + 1)

    @property
    def is_yang(self) -> bool:
        return self.yin_yang is YinYang.YANG

    @property
    def is_eum(self) -> bool:
        return self.yin_yang is YinYang.EUM
