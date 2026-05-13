"""60갑자(六十甲子) — 천간 10 × 지지 12의 60주기 조합."""

from __future__ import annotations

from .cheon_gan import CheonGan
from .ji_ji import JiJi


class GanJi:
    """60갑자 한 쌍 (천간+지지).

    유효한 60쌍은 천간/지지 인덱스 패리티가 같은 쌍.
    """

    __slots__ = ("cheon_gan", "ji_ji")

    def __init__(self, cheon_gan: CheonGan, ji_ji: JiJi) -> None:
        if not GanJi.is_valid_pair(cheon_gan, ji_ji):
            raise ValueError(
                f"60갑자 잘못된 조합: {cheon_gan.hanja}{ji_ji.hanja} "
                f"(천간 index {cheon_gan.index}, 지지 index {ji_ji.index} — 패리티 동일 필요)"
            )
        self.cheon_gan = cheon_gan
        self.ji_ji = ji_ji

    @classmethod
    def by_index(cls, index: int) -> GanJi:
        i = index % 60
        # bypass validation since by-index always produces a valid pair
        obj = object.__new__(cls)
        obj.cheon_gan = CheonGan.by_index(i)
        obj.ji_ji = JiJi.by_index(i)
        return obj

    @classmethod
    def from_hanja(cls, hanja: str) -> GanJi | None:
        if len(hanja) != 2:
            return None
        c = CheonGan.from_hanja(hanja[0])
        j = JiJi.from_hanja(hanja[1])
        if c is None or j is None:
            return None
        if not cls.is_valid_pair(c, j):
            return None
        return cls(c, j)

    @staticmethod
    def is_valid_pair(cheon_gan: CheonGan, ji_ji: JiJi) -> bool:
        return (cheon_gan.index % 2) == (ji_ji.index % 2)

    @property
    def index(self) -> int:
        """60갑자 인덱스 (0=甲子, …, 59=癸亥). 닫힌 형식 (c·6 − j·5) mod 60."""
        return (self.cheon_gan.index * 6 - self.ji_ji.index * 5) % 60

    @property
    def hanja(self) -> str:
        return f"{self.cheon_gan.hanja}{self.ji_ji.hanja}"

    @property
    def hangul(self) -> str:
        return f"{self.cheon_gan.hangul}{self.ji_ji.hangul}"

    @property
    def next(self) -> GanJi:
        return GanJi.by_index(self.index + 1)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, GanJi)
            and self.cheon_gan is other.cheon_gan
            and self.ji_ji is other.ji_ji
        )

    def __hash__(self) -> int:
        return hash((self.cheon_gan, self.ji_ji))

    def __repr__(self) -> str:
        return f"{self.hanja}({self.hangul})"

    def __str__(self) -> str:
        return self.__repr__()
