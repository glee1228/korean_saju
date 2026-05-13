"""旬空(공망) 산출 — 60갑자는 6개 旬(10갑자씩). 각 旬마다 공망 지지 2개."""

from __future__ import annotations

from .gan_ji import GanJi
from .ji_ji import JiJi


class XunGong:
    """일주 기준 공망 계산기."""

    @staticmethod
    def xun_start_index(day_pillar: GanJi) -> int:
        """일주가 속한 旬의 시작 60갑자 인덱스 (0, 10, 20, 30, 40, 50)."""
        return (day_pillar.index // 10) * 10

    @staticmethod
    def kong_mang_for(day_pillar: GanJi) -> tuple[JiJi, JiJi]:
        """일주의 旬空 지지 2개."""
        start = XunGong.xun_start_index(day_pillar)
        start_branch_idx = start % 12
        kong1 = (start_branch_idx + 10) % 12
        kong2 = (start_branch_idx + 11) % 12
        return (JiJi.by_index(kong1), JiJi.by_index(kong2))
