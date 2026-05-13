"""12신살(十二神煞) — 12지지 1:1 매핑.

기준 (일지 또는 연지) 삼합 그룹의 첫 지지(寅·申·巳·亥)에서 -3한 지지가 겁살,
이후 시계방향으로 12신살 순서.
"""

from __future__ import annotations

from enum import Enum

from .ji_ji import JiJi


class Sibisinsal(Enum):
    GEOPSAL = ("劫煞", "겁살", None,
               "외부에서 오는 충격·강제 이동·재물 손실 가능. 대비하면 위험을 줄일 수 있습니다.")
    JAESAL = ("災煞", "재살", "수옥살",
              "재난·구설·갇힘의 기운. 신중함과 인내가 필요한 시기일 수 있습니다.")
    CHEONSAL = ("天煞", "천살", None,
                "하늘에서 오는 시련 — 부모·윗사람과의 갈등 또는 천재지변. 겸손함이 도움 됩니다.")
    JISAL = ("地煞", "지살", None,
             "이동·이사·여행의 기운. 활동성이 높고 새로운 환경 적응에 적합합니다.")
    YEONSAL = ("年煞", "연살", "도화살",
               "도화(桃花)의 또 다른 이름 — 매력·인기·이성 관계가 활발합니다. 절제 필요할 수 있습니다.")
    WOLSAL = ("月煞", "월살", "고초살",
              "정체·무기력의 기운 — 메마른 땅에 달빛이 비치듯 고생 끝에 얻는 반사이익.")
    MANGSINSAL = ("亡神煞", "망신살", None,
                  "명예 손상·실수의 가능성. 언행 신중함이 보호가 됩니다.")
    JANGSEONGSAL = ("將星煞", "장성살", None,
                    "권위·출세·리더십의 별. 책임감과 함께 발휘하면 큰 성취가 가능합니다.")
    BANANSAL = ("攀鞍煞", "반안살", None,
                "명예·승진·말 안장에 오르는 기운 — 도움받아 올라서는 시기.")
    YEOKMASAL = ("驛馬煞", "역마살", None,
                 "이동·여행·해외·변동의 기운. 한곳에 머물기보단 움직임이 활력입니다.")
    YUKHAESAL = ("六害煞", "육해살", None,
                 "방해·시기·질투의 기운. 인간관계에 신중함이 필요할 수 있습니다.")
    HWAGAESAL = ("華蓋煞", "화개살", None,
                 "예술·종교·고독의 별 — 영적 깊이와 창조성. 내면 탐구에 적합합니다.")

    def __init__(
        self, hanja: str, hangul: str, alias: str | None, description: str
    ) -> None:
        self.hanja = hanja
        self.hangul = hangul
        self.alias = alias
        self.description = description


_IN_O_SUL_GROUP = frozenset({JiJi.IN, JiJi.O, JiJi.SUL})
_SIN_JA_JIN_GROUP = frozenset({JiJi.SIN, JiJi.JA, JiJi.JIN})
_SA_YU_CHUK_GROUP = frozenset({JiJi.SA, JiJi.YU, JiJi.CHUK})


def _group_start(ref: JiJi) -> int:
    if ref in _IN_O_SUL_GROUP:
        return JiJi.IN.index
    if ref in _SIN_JA_JIN_GROUP:
        return JiJi.SIN.index
    if ref in _SA_YU_CHUK_GROUP:
        return JiJi.SA.index
    return JiJi.HAE.index  # 亥卯未


class SibisinsalCalculator:
    """12신살 계산기."""

    @staticmethod
    def for_branch(reference: JiJi, target: JiJi) -> Sibisinsal:
        """[reference] (일지·연지) 기준 [target] 지지의 12신살."""
        group_start = _group_start(reference)
        geop_idx = (group_start - 3 + 12) % 12
        ship_idx = (target.index - geop_idx + 12) % 12
        return list(Sibisinsal)[ship_idx]
