"""십이운성(十二運星) — 일간 + 12지지로 결정되는 12단계 강약 사이클.

양일간: 장생 위치에서 순행. 음일간: 장생 위치에서 역행.
"""

from __future__ import annotations

from enum import Enum

from .cheon_gan import CheonGan
from .ji_ji import JiJi


class Sibiunseong(Enum):
    JANGSAENG = ("長生", "장생",
                 "새로운 시작과 성장의 단계 — 어린 잠재력이 펼쳐지는 시기입니다. 학습·창업 등 토대 만들기에 유리할 수 있습니다.")
    MOKYOK = ("沐浴", "목욕",
              "변화·정돈의 시기 — 욕망과 매력이 드러나지만 흔들림도 큰 단계. 도화 기운이 함께 합니다.")
    GWANDAE = ("冠帶", "관대",
               "성년식의 단계 — 자기 정체성을 갖추고 사회로 나가는 자립의 시기. 책임감이 자라납니다.")
    IMGWAN = ("臨官", "임관",
              "능력이 자리잡는 단계 — 일·관직에서 실력을 발휘하기 좋은 시기일 수 있습니다.")
    JEWANG = ("帝旺", "제왕",
              "절정의 단계 — 권력·명예·역량 최고조. 다만 자만하지 않을 때 안정적입니다.")
    SWAE = ("衰", "쇠",
            "쇠퇴의 시작 — 절정을 지나 차분해지는 시기. 무리하지 않으면 안정적일 수 있습니다.")
    BYUNG = ("病", "병",
             "병약의 시기 — 활동성은 줄지만 사색·치유·내면 성장에 적합합니다.")
    SA = ("死", "사",
          "정지의 단계 — 외적 활동 마무리·내적 성숙. 마무리·전환의 시기입니다.")
    MYO = ("墓", "묘",
           "저장의 단계 — 보이지 않는 곳에 잠재력 축적. 때가 오면 발휘됩니다.")
    JEOL = ("絕", "절",
            "단절·전환의 단계 — 모든 것이 비워지고 새로 시작되기 직전입니다.")
    TAE = ("胎", "태",
           "잉태의 단계 — 새로운 기운이 만들어지는 시기. 미세하지만 잠재력이 큽니다.")
    YANG = ("養", "양",
            "양육의 단계 — 보호받으며 천천히 자라나는 시기. 조급함 없이 기르면 좋습니다.")

    def __init__(self, hanja: str, hangul: str, description: str) -> None:
        self.hanja = hanja
        self.hangul = hangul
        self.description = description


# 일간별 장생 위치 (지지).
_JANGSAENG_POSITION: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.HAE,
    CheonGan.EUL: JiJi.O,
    CheonGan.BYEONG: JiJi.IN,
    CheonGan.JEONG: JiJi.YU,
    CheonGan.MU: JiJi.IN,
    CheonGan.GI: JiJi.YU,
    CheonGan.GYEONG: JiJi.SA,
    CheonGan.SIN: JiJi.JA,
    CheonGan.IM: JiJi.SIN,
    CheonGan.GYE: JiJi.MYO,
}


class SibiunseongCalculator:
    """일간 기준 십이운성 계산기."""

    @staticmethod
    def for_ji_ji(day_stem: CheonGan, target: JiJi) -> Sibiunseong:
        jangsaeng_idx = _JANGSAENG_POSITION[day_stem].index
        target_idx = target.index
        step = 1 if day_stem.is_yang else -1
        phase = (target_idx - jangsaeng_idx) * step
        phase = ((phase % 12) + 12) % 12
        return list(Sibiunseong)[phase]
