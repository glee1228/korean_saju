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

본 라이브러리는 **한국천문연구원(KASI) 공식 데이터**를 임베드하고, 데이터 범위 밖은 Meeus 천문 계산기로 보충한다. 모든 알고리즘은 1867개 음력 월 KASI 전수 검증 + 339개 단위 테스트를 통과한 Dart 구현을 1:1 포팅했다.

### 데이터 소스별 정밀도

| 데이터 | 범위 | 정확도 | 비고 |
|---|---|---|---|
| **KASI 음력** | 1900–2050 | **분 단위 (한국 표준)** | 1867개 월 전수 임베드, 일진·세차 KASI 값 그대로 |
| **KASI 24절기** | 2000–2027 | **분 단위 (한국 표준)** | 672개 절기 시각 임베드 |
| Meeus fallback (절기) | 1900–2150 | KASI 대비 평균 **±4.5분**, 최대 **±23분** | low-precision 공식, ΔT 다항식 ≤0.5초 |
| 진태양시(AST) 보정 | — | 경도 4분/1° 정밀, 균시차 미적용 (명리 표준) | KST 동경 135° 기준 |
| ΔT (Terrestrial Time) | 1900–2150 | **≤ 0.5초** | Espenak/Meeus 다항식 (NASA Eclipse Web Site) |

### 교차 검증 결과 (Dart 원본 프로젝트)

| 검증 항목 | 케이스 수 | 결과 |
|---|---|---|
| 양력 → 음력 변환 (vs `lunar` Dart pkg) | 25 | **23/25 일치** (불일치 2건은 lunar pkg 측 1일 오차 — KASI/한국 표준 우선) |
| 일진(日辰) 60갑자 | 25 | **25/25 일치** (100%) |
| 세차(歲次) 60갑자 | 25 | **25/25 일치** (100%) |
| 24절기 KASI vs lunar pkg | 120 | 평균 차이 27초, 95th 32초 |
| 24절기 KASI vs Meeus (자체) | 120 | 평균 차이 4.5분, 95th 9분 |
| 일주(日柱) — KASI 음력 1867개 월 1일 vs 우리 Julian Day 계산 | 1867 | **1867/1867 일치** (100%, 전수) |
| Dart 단위 테스트 (계산 + 분석 전체) | — | **339/339 통과** |
| Python smoke tests (이 패키지) | — | **12/12 통과** |

### 정밀도 설계 원칙

- **연주(年柱)**: 입춘(立春) 절입 시각 ±분 단위. 양력 1월 1일 ❌
- **월주(月柱)**: 12개 절(節) 절입 시각 기준. 음력 월 ❌
- **일주(日柱)**: AST(진태양시) 캘린더 날짜. KST 날짜 ❌ (0.1.1에서 fix)
- **시주(時柱)**: AST 12지시 + 五鼠遁. KST 직접 사용 ❌
- **자시 boundary**: AST 23:00 / 00:00 명시 분기 (야자시/조자시)
- **대운 시작 나이**: 출생~다음 절(順)/직전 절(逆) 일수 ÷ 3 + 잔여 개월
- **음력 윤달**: KASI 데이터 raw, 직접 수식 계산 금지

### 한계

- KASI 음력 데이터 범위 밖(1900 이전·2050 이후)은 음력 입력 사주 불가 (양력은 가능, Meeus accuracy로 fallback)
- 절기 Meeus fallback은 입춘/절 boundary 직전·직후 출생 시 최대 ±23분 오차 가능 — 해당 케이스에서 KASI 절기 데이터 확장 권장
- 균시차(equation of time)는 명리 전통상 미적용. 천문학적으로 더 정밀하게 필요하면 별도 보정 함수 추가 가능

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
