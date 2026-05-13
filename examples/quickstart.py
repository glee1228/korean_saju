"""korean-saju 빠른 사용 예제.

야자시/조자시 분리법 차이를 보여주고, 4기둥·십신·격국·용신을 출력.
"""

from __future__ import annotations

from datetime import datetime

from korean_saju import (
    Daewoon,
    Gender,
    Saju,
    SajuAnalysis,
    Sewoon,
    SolarTimeCorrection,
    load_bundled_data,
)


def main() -> None:
    # 패키지 내장 KASI 데이터 로드.
    _, solar_terms = load_bundled_data()

    # === 1. 기본 사용 ===
    birth = datetime(1990, 1, 1, 9, 0)  # 1990-01-01 09:00 KST
    saju = Saju.from_birth(
        kst_moment=birth,
        solar_terms=solar_terms,
        longitude=SolarTimeCorrection.SEOUL_LONGITUDE,
    )
    print("=" * 60)
    print(f"출생: {birth} KST (서울)")
    print(f"사주: {saju}")
    print(f"일간: {saju.day_stem.hangul}({saju.day_stem.hanja})")
    print(f"진태양시 보정: {SolarTimeCorrection.minutes_offset_from_kst(126.9784):.2f}분")

    analysis = SajuAnalysis(saju)
    print()
    print("천간 십신:", {p.hangul: s.hangul for p, s in analysis.cheon_gan_shipsin.items()})
    print("지지 십신:", {p.hangul: s.hangul for p, s in analysis.ji_ji_shipsin.items()})
    print("십이운성:", {p.hangul: s.hangul for p, s in analysis.sibiunseong.items()})
    print("정격:", analysis.jeonggyeok)
    print("용신:", analysis.yongsin)

    print()
    print("신살:")
    for detection in analysis.sinsal:
        print(f"  - {detection}")

    # === 2. 대운 ===
    daewoon = Daewoon.compute(saju=saju, gender=Gender.MALE, solar_terms=solar_terms, count=8)
    print()
    print(f"대운 ({'순행' if daewoon.forward else '역행'}, 시작까지 {daewoon.days_to_boundary:.1f}일):")
    for e in daewoon.entries:
        print(f"  - {e}")

    # === 3. 세운 ===
    sewoon = Sewoon.compute(
        saju=saju, solar_terms=solar_terms, center_year=2026, years_back=2, years_forward=5
    )
    print()
    print("세운 (2024–2031):")
    for e in sewoon:
        print(f"  - {e}")

    # === 4. 야자시 vs 조자시 분리 차이 ===
    boundary_birth = datetime(1994, 4, 28, 23, 40)
    print()
    print("=" * 60)
    print(f"경계 케이스: {boundary_birth} KST 서울")
    print(f"진태양시: {SolarTimeCorrection.to_apparent_solar_time(boundary_birth).time()}")
    yaja = Saju.from_birth(kst_moment=boundary_birth, solar_terms=solar_terms, yaja_si_separated=True)
    iljasi = Saju.from_birth(kst_moment=boundary_birth, solar_terms=solar_terms, yaja_si_separated=False)
    print(f"야자시 분리(기본): {yaja}")
    print(f"일자시(정자시 단일): {iljasi}")
    print(f"  차이 → 일주: {yaja.day_pillar.hanja} vs {iljasi.day_pillar.hanja}")


if __name__ == "__main__":
    main()
