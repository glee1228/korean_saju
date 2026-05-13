"""음력 날짜 값 객체."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LunarDate:
    year: int
    month: int
    day: int
    is_leap: bool = False

    def __str__(self) -> str:
        leap = "윤" if self.is_leap else ""
        return f"{self.year}년 {leap}{self.month}월 {self.day}일"
