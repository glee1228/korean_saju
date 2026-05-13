"""Smoke tests — package builds, 60갑자 cycle correct, yaja_si toggle works."""

from __future__ import annotations

from datetime import datetime

import pytest

from korean_saju import (
    CheonGan,
    GanJi,
    JiJi,
    Saju,
    SajuAnalysis,
    SolarTimeCorrection,
    XunGong,
    load_bundled_data,
)


@pytest.fixture(scope="module")
def solar_terms():
    _, terms = load_bundled_data()
    return terms


def test_imports_and_version() -> None:
    import korean_saju

    assert korean_saju.__version__


def test_60_galja_known_anchors() -> None:
    # 1984년 = 甲子年 (60갑자 index 0). 1984년 입춘 후 시점에서 검증.
    assert GanJi.by_index(0).hanja == "甲子"
    assert GanJi.by_index(40).hanja == "甲辰"
    assert GanJi.by_index(59).hanja == "癸亥"
    # Cycle wrap
    assert GanJi.by_index(60).hanja == "甲子"
    assert GanJi.by_index(-1).hanja == "癸亥"


def test_ganji_parity_rule() -> None:
    # 천간/지지 인덱스 패리티가 같아야 valid pair
    assert GanJi.is_valid_pair(CheonGan.GAP, JiJi.JA)  # 0/0
    assert not GanJi.is_valid_pair(CheonGan.GAP, JiJi.CHUK)  # 0/1
    with pytest.raises(ValueError):
        GanJi(CheonGan.GAP, JiJi.CHUK)


def test_solar_time_correction_seoul() -> None:
    # 서울(126.9784°E): KST 대비 약 -32.09분
    assert SolarTimeCorrection.minutes_offset_from_kst(126.9784) == pytest.approx(-32.0864)
    # 표준자오선
    assert SolarTimeCorrection.minutes_offset_from_kst(135.0) == 0.0


def test_xun_gong_kong_mang() -> None:
    # 갑자旬 (index 0) → 戌·亥 공망
    kong = XunGong.kong_mang_for(GanJi.by_index(0))
    assert set(kong) == {JiJi.SUL, JiJi.HAE}
    # 갑술旬 (index 10) → 申·酉 공망
    kong = XunGong.kong_mang_for(GanJi.by_index(10))
    assert set(kong) == {JiJi.SIN, JiJi.YU}


def test_basic_saju_smoke(solar_terms) -> None:
    saju = Saju.from_birth(
        kst_moment=datetime(1990, 1, 1, 9, 0),
        solar_terms=solar_terms,
    )
    # 1990-01-01 입춘 전 → 연주는 1989년 (己巳)
    assert saju.year_pillar.hanja == "己巳"
    # 일간이 결정되어야 함
    assert saju.day_stem is not None
    assert isinstance(saju.hour_pillar, GanJi)


def test_hour_unknown(solar_terms) -> None:
    saju = Saju.from_birth(
        kst_moment=datetime(1990, 1, 1, 12, 0),
        solar_terms=solar_terms,
        hour_known=False,
    )
    assert saju.hour_pillar is None


def test_yaja_si_separated_boundary(solar_terms) -> None:
    """야자시(23:00–24:00 진태양시) 경계에서 yaja_si_separated 토글이 일주를 바꿔야 함."""
    # 서울 출생 23:40 KST → 진태양시 ~23:08 (자시 영역)
    birth = datetime(1994, 4, 28, 23, 40)

    saju_separated = Saju.from_birth(
        kst_moment=birth, solar_terms=solar_terms, yaja_si_separated=True
    )
    saju_single = Saju.from_birth(
        kst_moment=birth, solar_terms=solar_terms, yaja_si_separated=False
    )

    # 두 모드 모두 시주는 같음 (자시는 항상 다음날 일간 기준 五鼠遁)
    assert saju_separated.hour_pillar == saju_single.hour_pillar
    # 일주는 달라야 함
    assert saju_separated.day_pillar != saju_single.day_pillar
    # single 모드의 일주가 separated 모드의 일주 + 1
    assert saju_single.day_pillar.index == (saju_separated.day_pillar.index + 1) % 60


def test_yaja_si_no_op_for_non_boundary_time(solar_terms) -> None:
    """진태양시가 23시 아닐 때는 yaja_si_separated 옵션이 결과에 영향 없어야 함."""
    birth = datetime(1990, 6, 15, 10, 0)  # 오시(午時)
    a = Saju.from_birth(kst_moment=birth, solar_terms=solar_terms, yaja_si_separated=True)
    b = Saju.from_birth(kst_moment=birth, solar_terms=solar_terms, yaja_si_separated=False)
    assert a.year_pillar == b.year_pillar
    assert a.month_pillar == b.month_pillar
    assert a.day_pillar == b.day_pillar
    assert a.hour_pillar == b.hour_pillar


def test_analysis_basic(solar_terms) -> None:
    saju = Saju.from_birth(
        kst_moment=datetime(1990, 1, 1, 9, 0), solar_terms=solar_terms
    )
    analysis = SajuAnalysis(saju)
    shipsin = analysis.cheon_gan_shipsin
    # 연·월간 십신이 존재
    assert len(shipsin) >= 2
    # 정격 결정됨
    assert analysis.jeonggyeok is not None
    # 용신 도출됨 (5오행 분류 모두 채워져야)
    yongsin = analysis.yongsin
    assert len(yongsin.classifications) == 5
