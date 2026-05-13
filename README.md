# korean-saju

한국 전통 사주(四柱) 만세력 — 야자시/조자시 분리법, 진태양시 보정, KASI 절기·음력 데이터 임베드.

> **사주(四柱)는 사실(fact), 해석은 의견(opinion).**
> 이 패키지는 사실(천간지지·오행·대운·세운·십신·격국·신살·용신 등)만 다룹니다. 해석은 다루지 않습니다.

## Features

- **4기둥(四柱) 계산** — 연주·월주·일주·시주
- **야자시(夜子時) / 조자시(朝子時) 분리법** — `yaja_si_separated` 옵션 (기본 True)
- **진태양시(眞太陽時) 출생지 경도 보정** — 표준 자오선 동경 135° 기준
- **입춘 절입 기준 연주, 절기 절입 기준 월주** — 양력 1월 1일·음력 월 아님
- **KASI(한국천문연구원) 데이터 임베드** — 음력 1900–2050, 절기 2000–2027
- 범위 밖 연도는 **Meeus 천문 계산기로 자동 fallback** (정확도 ±15분)
- 십신, 십이운성, 십이신살, 신살(길신 10 + 흉신 19)
- 격국(정격 8 + 건록격·양인격), 외격 16종
- 일간 강약, 조후(寒熱), 합충형파해, 용신 도출
- 대운, 세운, 60갑자 공망
- **순수 Python (의존성 0)** — Python 3.11+

## Install

```bash
pip install korean-saju
```

소스 빌드:

```bash
git clone https://github.com/glee1228/korean_saju.git
cd korean_saju
pip install -e .[dev]
```

## Quick start

```python
from datetime import datetime
from korean_saju import Saju, SajuAnalysis, load_bundled_data

# 패키지에 임베드된 KASI 데이터 로드
lunar, solar_terms = load_bundled_data()

# 출생 시각 (KST). naive 또는 tz-aware 모두 OK.
birth = datetime(1990, 1, 1, 9, 0)

saju = Saju.from_birth(
    kst_moment=birth,
    solar_terms=solar_terms,
    longitude=126.9784,           # 서울
    yaja_si_separated=True,        # 야자시 분리 (기본)
)
print(saju)
# 己巳(기사) 丙子(병자) 丙寅(병인) 癸巳(계사)

# 십신·격국·용신 등 분석
analysis = SajuAnalysis(saju)
print(analysis.jeonggyeok)         # 정격
print(analysis.yongsin)            # 용신
for s in analysis.sinsal:           # 신살 목록
    print(s)
```

## 야자시(夜子時) / 조자시(朝子時)

자시(子時) 영역은 **진태양시(AST) 기준** 으로 정의된다:

- **야자시(夜子時)**: AST **23:00–24:00** — 당일 자시 영역
- **조자시(朝子時)**: AST **00:00–01:00** — 다음날 자시 영역

시주 자시는 두 경우 모두 **다음날 일간** 기준 五鼠遁이라 동일하다. 차이는 **일주(日柱)** — `yaja_si_separated` 토글이 야자시의 일주를 결정한다 (조자시는 모드 무관).

### 1. 분리법 (`yaja_si_separated=True`, **기본**, 한국 명리 표준)

야자시는 AST **당일** 일주, 조자시는 AST **다음날** 일주 (자연 처리).

### 2. 정자시 단일 (`yaja_si_separated=False`)

야자시도 다음날 일주로 통합. 중국 자평 유파에 가까움.

> ⚠️ **일주·시주는 AST 캘린더 날짜 기준**. KST 기준으로 하면 longitude 보정으로 KST는 자정을 넘었지만 AST는 아직 어제인 경우 (KST 1990-01-02 00:10 서울 → AST 23:37 어제) 일주가 하루 어긋난다. (0.1.1에서 수정)

```python
# 1994-04-28 23:40 KST 서울 (진태양시 23:08)
birth = datetime(1994, 4, 28, 23, 40)

# 야자시 분리 (기본): 갑신일 + 병자시
s1 = Saju.from_birth(
    kst_moment=birth, solar_terms=solar_terms,
    yaja_si_separated=True,
)
print(s1.day_pillar.hanja, s1.hour_pillar.hanja)  # 甲申 丙子

# 일자시 (정자시 단일): 을유일 + 병자시
s2 = Saju.from_birth(
    kst_moment=birth, solar_terms=solar_terms,
    yaja_si_separated=False,
)
print(s2.day_pillar.hanja, s2.hour_pillar.hanja)  # 乙酉 丙子
```

`yaja_si_separated` 차이는 **AST 23:00–24:00 출생자**에서만 발생한다 (야자시 영역). 조자시(AST 00:00–01:00)는 두 모드가 동일한 결과를 낸다.

## 진태양시(眞太陽時)

KST는 동경 135° (일본 자오선) 기준. 서울(동경 126.98°)에서는 KST가 실제 태양시보다 ~32분 빠르다.
사주 시주(時柱)는 진태양시로 계산해야 정확하다.

```python
from korean_saju import SolarTimeCorrection

SolarTimeCorrection.minutes_offset_from_kst(126.9784)  # 서울 → -32.09분
SolarTimeCorrection.minutes_offset_from_kst(129.08)    # 부산 → -23.68분
```

## Accuracy

| 데이터 | 범위 | 정확도 |
|---|---|---|
| KASI 음력 | 1900–2050 | 표준 (분 단위) |
| KASI 절기 | 2000–2027 | 표준 (분 단위) |
| 천문 계산 (Meeus) fallback | 1900–2150 | ±15분 |
| 진태양시 보정 | — | 균시차 미적용 (평균 태양시까지만, 명리 표준) |

## API 개요

```python
from korean_saju import (
    # Core
    Saju, SajuAnalysis, SajuPosition,
    YearPillar, MonthPillar, DayPillar, HourPillar,
    SolarTermSource, SolarTimeCorrection,
    # Domain
    CheonGan, JiJi, GanJi, YinYang, OHaeng,
    Shipsin, Sibiunseong, Sibisinsal, Sinsal,
    # Analysis
    Daewoon, Sewoon, Gender,
    Gyeokguk, GyeokgukCalculator,
    IlganStrengthAnalyzer, IlganStrengthLevel,
    JohuAnalyzer, HapChungAnalyzer,
    OegyeokAnalyzer, OegyeokVerdict,
    YongsinDeriver, YongsinRole, YongsinMethod,
    XunGong, GongmangByPillar,
    # KASI loaders
    KasiLunarData, KasiSolarTerms,
    load_bundled_data, load_data_from_paths,
)
```

## Domain Glossary

| 용어 | 한자 | 의미 |
|---|---|---|
| 사주 | 四柱 | 생년월일시 4기둥 |
| 천간 | 天干 | 갑을병정무기경신임계 (10) |
| 지지 | 地支 | 자축인묘진사오미신유술해 (12) |
| 60갑자 | 六十甲子 | 천간×지지 60주기 |
| 절기 | 節氣 | 24절기 — 월주 기준 |
| 입춘 | 立春 | 연주 시작 기준 절기 |
| 진태양시 | 眞太陽時 | 출생지 경도 보정 시각 |
| 자시 | 子時 | 23:00~01:00 (12지시 첫 시간) |
| 야자시 | 夜子時 | AST 23:00~24:00 (당일 자시 영역) |
| 조자시 | 朝子時 | AST 00:00~01:00 (다음날 자시 영역) |
| 대운 | 大運 | 10년 단위 운세 흐름 |
| 세운 | 歲運 | 1년 단위 운세 |
| 십신 | 十神 | 비견·겁재·식신·상관·편재·정재·편관·정관·편인·정인 |
| 십이운성 | 十二運星 | 장생·목욕·관대·... 12단계 |
| 오행 | 五行 | 목화토금수 |
| 격국 | 格局 | 자평 8정격 + 건록·양인 |
| 외격 | 外格 | 화기·종격·일행득기·양신성상 (16종) |
| 용신 | 用神 | 사주를 가장 좋게 하는 오행 |
| 조후 | 調候 | 사주의 한열(寒熱) 조정 |

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- KASI(한국천문연구원) Open API — 절기·음력 데이터 원본
- Jean Meeus, *Astronomical Algorithms* — 절기 천문 계산 fallback
- Espenak/NASA Eclipse Web Site — ΔT 다항식
- 자평진전·연해자평 등 정통 명리 문헌 — 격국·용신 알고리즘
