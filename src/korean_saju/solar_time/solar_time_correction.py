"""진태양시(眞太陽時) 보정.

KST(동경 135°)와 출생지 경도의 차이를 분 단위로 보정.
명리에서는 균시차(equation of time)를 보통 생략하고 평균 태양시까지만 적용한다.
"""

from __future__ import annotations

from datetime import datetime, timedelta


class SolarTimeCorrection:
    """진태양시 변환 유틸 (전부 정적 메서드)."""

    # 한국 표준자오선 (동경 135°). 일본을 지남.
    KOREAN_STANDARD_MERIDIAN: float = 135.0

    # 서울 경도 — 기본값.
    SEOUL_LONGITUDE: float = 126.9784

    def __init__(self) -> None:
        raise TypeError("SolarTimeCorrection is a static utility class")

    @staticmethod
    def minutes_offset_from_kst(longitude: float) -> float:
        """출생지 longitude(동경 +, 서경 −)에서 KST 대비 분 단위 offset.

        음수: KST보다 늦음(서쪽). 양수: KST보다 빠름(동쪽).
        예: 서울(126.9784°E) → 대략 −32.09분.
        """
        return (longitude - SolarTimeCorrection.KOREAN_STANDARD_MERIDIAN) * 4.0

    @staticmethod
    def to_apparent_solar_time(
        kst_datetime: datetime,
        *,
        longitude: float = SEOUL_LONGITUDE,
    ) -> datetime:
        """KST datetime을 진태양시로 변환.

        반환된 datetime은 "보정된 시각" 의미상 마커일 뿐 실제 timezone 의미는 없음.
        사주 시주 계산에서 시·분 추출용으로만 사용.
        """
        offset_min = SolarTimeCorrection.minutes_offset_from_kst(longitude)
        return kst_datetime + timedelta(minutes=offset_min)
