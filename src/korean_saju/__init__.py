"""korean-saju — 한국 전통 사주(四柱) 만세력.

야자시/조자시 분리법, 진태양시 보정, KASI 음력/절기 데이터 임베드.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from .calendar.kasi_lunar_data import KasiLunarData, LunarMonthRecord
from .calendar.kasi_solar_terms import KasiSolarTerms
from .calendar.lunar_date import LunarDate
from .calendar.solar_term import SolarTerm, SolarTermType
from .calendar.solar_term_source import SolarTermSource
from .saju.cheon_gan import CheonGan
from .saju.daewoon import Daewoon, DaewoonEntry, Gender
from .saju.day_pillar import DayPillar
from .saju.gan_ji import GanJi
from .saju.gyeokguk import Gyeokguk, GyeokgukCalculator, GyeokgukResult
from .saju.hapchung import (
    ChungHyungDetection,
    ChungHyungKind,
    HapChungAnalyzer,
    HapDetection,
    HapKind,
)
from .saju.hour_pillar import HourPillar
from .saju.ilgan_strength import (
    IlganStrengthAnalyzer,
    IlganStrengthBreakdown,
    IlganStrengthLevel,
)
from .saju.ji_jang_gan import JiJangGanRole
from .saju.ji_ji import JiJi
from .saju.johu import JohuAnalysis, JohuAnalyzer
from .saju.month_pillar import MonthPillar
from .saju.o_haeng import OHaeng
from .saju.oegyeok import OegyeokAnalyzer, OegyeokResult, OegyeokType, OegyeokVerdict
from .saju.saju import Saju, SajuPosition
from .saju.saju_analysis import GongmangByPillar, SajuAnalysis
from .saju.sewoon import Sewoon, SewoonEntry
from .saju.shipsin import Shipsin, ShipsinCalculator
from .saju.sibisinsal import Sibisinsal, SibisinsalCalculator
from .saju.sibiunseong import Sibiunseong, SibiunseongCalculator
from .saju.sinsal import (
    Sinsal,
    SinsalCalculator,
    SinsalDetection,
    SinsalKind,
    SinsalLocation,
)
from .saju.xun_gong import XunGong
from .saju.year_pillar import YearPillar
from .saju.yin_yang import YinYang
from .saju.yongsin import YongsinDeriver, YongsinMethod, YongsinResult, YongsinRole
from .solar_time.solar_time_correction import SolarTimeCorrection

__all__ = [
    "CheonGan",
    "ChungHyungDetection",
    "ChungHyungKind",
    "Daewoon",
    "DaewoonEntry",
    "DayPillar",
    "GanJi",
    "Gender",
    "GongmangByPillar",
    "Gyeokguk",
    "GyeokgukCalculator",
    "GyeokgukResult",
    "HapChungAnalyzer",
    "HapDetection",
    "HapKind",
    "HourPillar",
    "IlganStrengthAnalyzer",
    "IlganStrengthBreakdown",
    "IlganStrengthLevel",
    "JiJangGanRole",
    "JiJi",
    "JohuAnalysis",
    "JohuAnalyzer",
    "KasiLunarData",
    "KasiSolarTerms",
    "LunarDate",
    "LunarMonthRecord",
    "MonthPillar",
    "OHaeng",
    "OegyeokAnalyzer",
    "OegyeokResult",
    "OegyeokType",
    "OegyeokVerdict",
    "Saju",
    "SajuAnalysis",
    "SajuPosition",
    "Sewoon",
    "SewoonEntry",
    "Shipsin",
    "ShipsinCalculator",
    "Sibisinsal",
    "SibisinsalCalculator",
    "Sibiunseong",
    "SibiunseongCalculator",
    "Sinsal",
    "SinsalCalculator",
    "SinsalDetection",
    "SinsalKind",
    "SinsalLocation",
    "SolarTerm",
    "SolarTermSource",
    "SolarTermType",
    "SolarTimeCorrection",
    "XunGong",
    "YearPillar",
    "YinYang",
    "YongsinDeriver",
    "YongsinMethod",
    "YongsinResult",
    "YongsinRole",
    "load_bundled_data",
]

__version__ = "0.1.0"


def load_bundled_data() -> tuple[KasiLunarData, SolarTermSource]:
    """패키지에 임베드된 KASI 데이터를 로드해 (음력, 절기 source) 반환.

    Returns:
        (KasiLunarData, SolarTermSource) — 음력 1900–2050, 절기 2000–2027.
        절기 source는 범위 밖 연도에 대해 Meeus 천문 계산기로 자동 fallback.
    """
    pkg = resources.files("korean_saju") / "data"
    lunar_path = pkg / "kasi_lunar_1900_2050.json"
    terms_path = pkg / "kasi_solar_terms_2000_2027.json"
    lunar = KasiLunarData.from_json(lunar_path.read_text(encoding="utf-8"))
    kasi_terms = KasiSolarTerms.from_json(terms_path.read_text(encoding="utf-8"))
    return lunar, SolarTermSource(kasi=kasi_terms)


def load_data_from_paths(
    lunar_json_path: str | Path,
    solar_terms_json_path: str | Path,
) -> tuple[KasiLunarData, SolarTermSource]:
    """디스크의 KASI JSON 파일을 로드 (커스텀 데이터셋용)."""
    lunar = KasiLunarData.from_json(Path(lunar_json_path).read_text(encoding="utf-8"))
    kasi_terms = KasiSolarTerms.from_json(
        Path(solar_terms_json_path).read_text(encoding="utf-8")
    )
    return lunar, SolarTermSource(kasi=kasi_terms)
