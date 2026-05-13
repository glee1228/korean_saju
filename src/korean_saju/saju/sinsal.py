"""신살(神煞) — 길신 10개 + 흉신 19개. 사주 4기둥에서 위치별 검출."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cheon_gan import CheonGan
from .ji_ji import JiJi
from .saju import Saju
from .shipsin import Shipsin, ShipsinCalculator


class SinsalLocation(Enum):
    YEAR_STEM = "연간"
    YEAR_BRANCH = "연지"
    MONTH_STEM = "월간"
    MONTH_BRANCH = "월지"
    DAY_STEM = "일간"
    DAY_BRANCH = "일지"
    HOUR_STEM = "시간"
    HOUR_BRANCH = "시지"

    def __init__(self, label: str) -> None:
        self.label = label


class SinsalKind(Enum):
    GILSIN = "gilsin"
    HYUNGSIN = "hyungsin"


class Sinsal(Enum):
    # === 길신 ===
    CHEON_EUL_GWIIN = ("天乙貴人", "천을귀인", SinsalKind.GILSIN,
                       "위기 상황에서 귀인의 도움을 받아 화가 복으로 변함")
    MUN_CHANG_GWIIN = ("文昌貴人", "문창귀인", SinsalKind.GILSIN,
                       "지혜롭고 문학적 재능이 뛰어나며 학업 성취가 높음")
    AM_ROK = ("暗祿", "암록", SinsalKind.GILSIN,
              "보이지 않는 곳에서 돕는 손길, 경제적 위기 탈출")
    GEUM_YEO = ("金輿", "금여", SinsalKind.GILSIN,
                "귀한 신분, 배우자의 덕이 있고 평온한 삶")
    CHEON_JU_GWIIN = ("天廚貴人", "천주귀인", SinsalKind.GILSIN,
                      "하늘의 주방. 먹을 복이 타고났으며 경제적 여유")
    HAK_DANG_GWIIN = ("學堂貴人", "학당귀인", SinsalKind.GILSIN,
                      "배움에 능하고 지적이며, 가르치는 직업에 유리")
    MUN_GOK_GWIIN = ("文曲貴人", "문곡귀인", SinsalKind.GILSIN,
                     "문학적 재능과 예술적 감각, 아이디어가 뛰어남")
    TAE_GEUK_GWIIN = ("太極貴人", "태극귀인", SinsalKind.GILSIN,
                      "초년에 고생해도 결국 큰 성취를 이루고 복을 받음. 종교·철학적 명예")
    BOK_SIN = ("福神", "복신", SinsalKind.GILSIN,
               "예상치 못한 행운이 따르며 흉한 일을 막아줌")
    CHEON_EUI_SEONG = ("天醫星", "천의성", SinsalKind.GILSIN,
                       "하늘의 의사. 의료·상담·교육 등 남을 살리는 직업")

    # === 흉신 ===
    BAEKHO_DAE_SAL = ("白虎大殺", "백호대살", SinsalKind.HYUNGSIN,
                      "호랑이에게 물려가듯 갑작스러운 사고나 폭발적인 힘")
    GOEGANG_SAL = ("魁罡殺", "괴강살", SinsalKind.HYUNGSIN,
                   "총명하고 결단력이 강하며 대중을 이끄는 카리스마")
    YANG_IN_SAL = ("陽刃殺", "양인살", SinsalKind.HYUNGSIN,
                   "극단적인 추진력과 고집, 전문적인 기술과 권력")
    WONJIN_SAL = ("怨嗔殺", "원진살", SinsalKind.HYUNGSIN,
                  "이유 없이 서로 미워하고 원망하며 소통이 꼬임")
    GWIMUN_GWAN_SAL = ("鬼門關殺", "귀문관살", SinsalKind.HYUNGSIN,
                       "신경이 예민하고 직관력이 뛰어나며 집착이 강함")
    HYEON_CHIM = ("懸針殺", "현침살", SinsalKind.HYUNGSIN,
                  "바늘을 든 형상. 정밀한 기술이나 날카로운 언변")
    HONG_YEOM_SAL = ("紅艶殺", "홍염살", SinsalKind.HYUNGSIN,
                     "도화보다 짙고 개인적인 매력으로 사람을 홀림")
    GO_RAN_SAL = ("孤鸞殺", "고란살", SinsalKind.HYUNGSIN,
                  "외로운 새의 울음. 배우자 운이 약하고 홀로 지냄. 여성에게 주로 해당")
    TANG_HWA_SAL = ("湯火殺", "탕화살", SinsalKind.HYUNGSIN,
                    "화상·중독 주의. 감정 기복이 심해 폭발할 위험")
    SANG_MUN_SAL = ("喪門殺", "상문살", SinsalKind.HYUNGSIN,
                    "집안에 슬픈 일이나 본인·주변의 건강 악화 주의")
    JO_GAEK_SAL = ("弔客殺", "조객살", SinsalKind.HYUNGSIN,
                   "조문할 일이 생기거나 집안에 우환")
    GYEOK_GAK = ("隔角殺", "격각살", SinsalKind.HYUNGSIN,
                 "육친과의 인연이 박하고 고향을 떠나 떠돌 수 있음")
    HYO_SIN_SAL = ("梟神殺", "효신살", SinsalKind.HYUNGSIN,
                   "어머니와의 갈등이나 집착, 고부 갈등의 소지")
    GO_SIN_SAL = ("孤辰殺", "고신살", SinsalKind.HYUNGSIN,
                  "홀아비 살. 배우자와의 인연이 약하고 외로움")
    GWA_SUK_SAL = ("寡宿殺", "과숙살", SinsalKind.HYUNGSIN,
                   "과부 살. 배우자와의 인연이 약하고 외로움")
    CHEON_RA_JI_MANG = ("天羅地網", "천라지망", SinsalKind.HYUNGSIN,
                        "하늘과 땅의 그물. 일이 막히니 정신적 성취가 필요")
    NAK_JEONG_GWAN_SAL = ("落井關殺", "낙정관살", SinsalKind.HYUNGSIN,
                          "구덩이에 빠짐. 갑작스러운 사고나 인간관계의 배신")
    GEUP_GAK_SAL = ("急脚殺", "급각살", SinsalKind.HYUNGSIN,
                    "다리를 다치거나 신경통 등 정형외과적 질환 주의")
    CHEOL_SA_GYE = ("鐵蛇戒", "철사계", SinsalKind.HYUNGSIN,
                    "쇠나 뱀에 물림. 몸에 칼을 대는 수술수나 흉터")

    def __init__(
        self, hanja: str, hangul: str, kind: SinsalKind, description: str
    ) -> None:
        self.hanja = hanja
        self.hangul = hangul
        self.kind = kind
        self.description = description

    @property
    def is_gilsin(self) -> bool:
        return self.kind is SinsalKind.GILSIN

    @property
    def is_hyungsin(self) -> bool:
        return self.kind is SinsalKind.HYUNGSIN


@dataclass(frozen=True, slots=True)
class SinsalDetection:
    sinsal: Sinsal
    locations: tuple[SinsalLocation, ...]

    def __str__(self) -> str:
        locs = ",".join(l.label for l in self.locations)
        return f"{self.sinsal.hangul}({self.sinsal.hanja}) @ {locs}"


# Helper tables.
_CHEON_EUL_TARGETS: dict[CheonGan, tuple[JiJi, ...]] = {
    CheonGan.GAP: (JiJi.CHUK, JiJi.MI),
    CheonGan.MU: (JiJi.CHUK, JiJi.MI),
    CheonGan.GYEONG: (JiJi.CHUK, JiJi.MI),
    CheonGan.EUL: (JiJi.JA, JiJi.SIN),
    CheonGan.GI: (JiJi.JA, JiJi.SIN),
    CheonGan.BYEONG: (JiJi.HAE, JiJi.YU),
    CheonGan.JEONG: (JiJi.HAE, JiJi.YU),
    CheonGan.IM: (JiJi.SA, JiJi.MYO),
    CheonGan.GYE: (JiJi.SA, JiJi.MYO),
    CheonGan.SIN: (JiJi.IN, JiJi.O),
}

_MUN_CHANG_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.SA, CheonGan.EUL: JiJi.O, CheonGan.BYEONG: JiJi.SIN,
    CheonGan.JEONG: JiJi.YU, CheonGan.MU: JiJi.SIN, CheonGan.GI: JiJi.YU,
    CheonGan.GYEONG: JiJi.HAE, CheonGan.SIN: JiJi.JA,
    CheonGan.IM: JiJi.IN, CheonGan.GYE: JiJi.MYO,
}

_AM_ROK_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.HAE, CheonGan.EUL: JiJi.SUL, CheonGan.BYEONG: JiJi.SIN,
    CheonGan.JEONG: JiJi.MI, CheonGan.MU: JiJi.SIN, CheonGan.GI: JiJi.MI,
    CheonGan.GYEONG: JiJi.SA, CheonGan.SIN: JiJi.JIN,
    CheonGan.IM: JiJi.IN, CheonGan.GYE: JiJi.CHUK,
}

_GEUM_YEO_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.JIN, CheonGan.EUL: JiJi.SA, CheonGan.BYEONG: JiJi.MI,
    CheonGan.JEONG: JiJi.SIN, CheonGan.MU: JiJi.MI, CheonGan.GI: JiJi.SIN,
    CheonGan.GYEONG: JiJi.SUL, CheonGan.SIN: JiJi.HAE,
    CheonGan.IM: JiJi.CHUK, CheonGan.GYE: JiJi.IN,
}

_CHEON_JU_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.SA, CheonGan.EUL: JiJi.O, CheonGan.BYEONG: JiJi.SA,
    CheonGan.JEONG: JiJi.O, CheonGan.MU: JiJi.SIN, CheonGan.GI: JiJi.YU,
    CheonGan.GYEONG: JiJi.HAE, CheonGan.SIN: JiJi.JA,
    CheonGan.IM: JiJi.IN, CheonGan.GYE: JiJi.MYO,
}

_HAK_DANG_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.HAE, CheonGan.EUL: JiJi.O, CheonGan.BYEONG: JiJi.IN,
    CheonGan.MU: JiJi.IN, CheonGan.JEONG: JiJi.YU, CheonGan.GI: JiJi.YU,
    CheonGan.GYEONG: JiJi.SA, CheonGan.SIN: JiJi.JA,
    CheonGan.IM: JiJi.SIN, CheonGan.GYE: JiJi.MYO,
}

_MUN_GOK_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.HAE, CheonGan.EUL: JiJi.JA, CheonGan.BYEONG: JiJi.IN,
    CheonGan.JEONG: JiJi.MYO, CheonGan.MU: JiJi.IN, CheonGan.GI: JiJi.MYO,
    CheonGan.GYEONG: JiJi.SA, CheonGan.SIN: JiJi.O,
    CheonGan.IM: JiJi.SIN, CheonGan.GYE: JiJi.YU,
}

_TAE_GEUK_TARGETS: dict[CheonGan, tuple[JiJi, ...]] = {
    CheonGan.GAP: (JiJi.JA, JiJi.O),
    CheonGan.EUL: (JiJi.JA, JiJi.O),
    CheonGan.BYEONG: (JiJi.MYO, JiJi.YU),
    CheonGan.JEONG: (JiJi.MYO, JiJi.YU),
    CheonGan.MU: (JiJi.JIN, JiJi.SUL, JiJi.CHUK, JiJi.MI),
    CheonGan.GI: (JiJi.JIN, JiJi.SUL, JiJi.CHUK, JiJi.MI),
    CheonGan.GYEONG: (JiJi.IN, JiJi.HAE),
    CheonGan.SIN: (JiJi.IN, JiJi.HAE),
    CheonGan.IM: (JiJi.SA, JiJi.SIN),
    CheonGan.GYE: (JiJi.SA, JiJi.SIN),
}

_YANG_IN_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.MYO, CheonGan.BYEONG: JiJi.O, CheonGan.MU: JiJi.O,
    CheonGan.GYEONG: JiJi.YU, CheonGan.IM: JiJi.JA,
}

_HONG_YEOM_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.O, CheonGan.EUL: JiJi.O, CheonGan.BYEONG: JiJi.IN,
    CheonGan.JEONG: JiJi.IN, CheonGan.MU: JiJi.JIN, CheonGan.GI: JiJi.JIN,
    CheonGan.GYEONG: JiJi.SUL, CheonGan.SIN: JiJi.SUL,
    CheonGan.IM: JiJi.JA, CheonGan.GYE: JiJi.JA,
}

_NAK_JEONG_TARGETS: dict[CheonGan, JiJi] = {
    CheonGan.GAP: JiJi.SA, CheonGan.GI: JiJi.SA,
    CheonGan.EUL: JiJi.JA, CheonGan.GYEONG: JiJi.JA,
    CheonGan.BYEONG: JiJi.SIN, CheonGan.SIN: JiJi.SIN,
    CheonGan.JEONG: JiJi.SUL, CheonGan.IM: JiJi.SUL,
    CheonGan.MU: JiJi.MYO, CheonGan.GYE: JiJi.MYO,
}

_BAEKHO_PILLARS = frozenset({"甲辰", "乙未", "丙戌", "丁丑", "戊辰", "壬戌", "癸丑"})
_GOEGANG_PILLARS = frozenset({"庚辰", "庚戌", "壬辰", "壬戌", "戊戌", "戊辰"})
_GO_RAN_PILLARS = frozenset({"甲寅", "乙巳", "丙午", "丁巳", "戊申", "辛亥", "壬子"})

_GWIMUN_PAIRS: tuple[frozenset[JiJi], ...] = (
    frozenset({JiJi.JA, JiJi.MI}),
    frozenset({JiJi.CHUK, JiJi.O}),
    frozenset({JiJi.IN, JiJi.YU}),
    frozenset({JiJi.MYO, JiJi.SIN}),
    frozenset({JiJi.JIN, JiJi.HAE}),
    frozenset({JiJi.SA, JiJi.SUL}),
)

_SHARP_STEMS = frozenset({CheonGan.GAP, CheonGan.SIN})
_SHARP_BRANCHES = frozenset({JiJi.MYO, JiJi.SIN})


def _branches_matching(saju: Saju, targets: tuple[JiJi, ...] | list[JiJi]) -> list[SinsalLocation]:
    targets_set = frozenset(targets)
    result: list[SinsalLocation] = []
    if saju.year_pillar.ji_ji in targets_set:
        result.append(SinsalLocation.YEAR_BRANCH)
    if saju.month_pillar.ji_ji in targets_set:
        result.append(SinsalLocation.MONTH_BRANCH)
    if saju.day_pillar.ji_ji in targets_set:
        result.append(SinsalLocation.DAY_BRANCH)
    if saju.hour_pillar is not None and saju.hour_pillar.ji_ji in targets_set:
        result.append(SinsalLocation.HOUR_BRANCH)
    return result


def _branch_pairs_triggered(
    saju: Saju, pairs: tuple[frozenset[JiJi], ...]
) -> list[SinsalLocation]:
    branches: dict[JiJi, SinsalLocation] = {
        saju.year_pillar.ji_ji: SinsalLocation.YEAR_BRANCH,
        saju.month_pillar.ji_ji: SinsalLocation.MONTH_BRANCH,
        saju.day_pillar.ji_ji: SinsalLocation.DAY_BRANCH,
    }
    if saju.hour_pillar is not None:
        branches[saju.hour_pillar.ji_ji] = SinsalLocation.HOUR_BRANCH
    keys = set(branches.keys())
    result: list[SinsalLocation] = []
    for pair in pairs:
        if pair.issubset(keys):
            for j in pair:
                result.append(branches[j])
    return result


def _all_locations(saju: Saju) -> list[SinsalLocation]:
    result = [
        SinsalLocation.YEAR_STEM, SinsalLocation.YEAR_BRANCH,
        SinsalLocation.MONTH_STEM, SinsalLocation.MONTH_BRANCH,
        SinsalLocation.DAY_STEM, SinsalLocation.DAY_BRANCH,
    ]
    if saju.hour_pillar is not None:
        result.extend([SinsalLocation.HOUR_STEM, SinsalLocation.HOUR_BRANCH])
    return result


def _stem_at(saju: Saju, loc: SinsalLocation) -> CheonGan | None:
    if loc is SinsalLocation.YEAR_STEM:
        return saju.year_pillar.cheon_gan
    if loc is SinsalLocation.MONTH_STEM:
        return saju.month_pillar.cheon_gan
    if loc is SinsalLocation.DAY_STEM:
        return saju.day_pillar.cheon_gan
    if loc is SinsalLocation.HOUR_STEM:
        return saju.hour_pillar.cheon_gan if saju.hour_pillar else None
    return None


def _branch_at(saju: Saju, loc: SinsalLocation) -> JiJi | None:
    if loc is SinsalLocation.YEAR_BRANCH:
        return saju.year_pillar.ji_ji
    if loc is SinsalLocation.MONTH_BRANCH:
        return saju.month_pillar.ji_ji
    if loc is SinsalLocation.DAY_BRANCH:
        return saju.day_pillar.ji_ji
    if loc is SinsalLocation.HOUR_BRANCH:
        return saju.hour_pillar.ji_ji if saju.hour_pillar else None
    return None


def _detect_cheon_eul(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, _CHEON_EUL_TARGETS[saju.day_stem])


def _detect_mun_chang(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_MUN_CHANG_TARGETS[saju.day_stem]])


def _detect_am_rok(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_AM_ROK_TARGETS[saju.day_stem]])


def _detect_geum_yeo(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_GEUM_YEO_TARGETS[saju.day_stem]])


def _detect_cheon_ju(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_CHEON_JU_TARGETS[saju.day_stem]])


def _detect_hak_dang(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_HAK_DANG_TARGETS[saju.day_stem]])


def _detect_mun_gok(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_MUN_GOK_TARGETS[saju.day_stem]])


def _detect_tae_geuk(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, _TAE_GEUK_TARGETS[saju.day_stem])


def _detect_bok_sin(saju: Saju) -> list[SinsalLocation]:
    # v1 단순 정의: 천을귀인 매칭 시 복신도 함께
    return _detect_cheon_eul(saju)


def _detect_cheon_eui(saju: Saju) -> list[SinsalLocation]:
    month_idx = saju.month_pillar.ji_ji.index
    target = JiJi.by_index(month_idx - 1 + 12)
    return _branches_matching(saju, [target])


def _detect_baekho_dae(saju: Saju) -> list[SinsalLocation]:
    return [SinsalLocation.DAY_BRANCH] if saju.day_pillar.hanja in _BAEKHO_PILLARS else []


def _detect_goegang(saju: Saju) -> list[SinsalLocation]:
    return [SinsalLocation.DAY_BRANCH] if saju.day_pillar.hanja in _GOEGANG_PILLARS else []


def _detect_yang_in(saju: Saju) -> list[SinsalLocation]:
    target = _YANG_IN_TARGETS.get(saju.day_stem)
    if target is None:
        return []
    return _branches_matching(saju, [target])


def _detect_wonjin(saju: Saju) -> list[SinsalLocation]:
    return _branch_pairs_triggered(saju, _GWIMUN_PAIRS)


def _detect_gwimun_gwan(saju: Saju) -> list[SinsalLocation]:
    return _branch_pairs_triggered(saju, _GWIMUN_PAIRS)


def _detect_hyeon_chim(saju: Saju) -> list[SinsalLocation]:
    result: list[SinsalLocation] = []
    for loc in _all_locations(saju):
        s = _stem_at(saju, loc)
        b = _branch_at(saju, loc)
        if s is not None and s in _SHARP_STEMS:
            result.append(loc)
        if b is not None and b in _SHARP_BRANCHES:
            result.append(loc)
    return result


def _detect_hong_yeom(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_HONG_YEOM_TARGETS[saju.day_stem]])


def _detect_go_ran(saju: Saju) -> list[SinsalLocation]:
    return [SinsalLocation.DAY_BRANCH] if saju.day_pillar.hanja in _GO_RAN_PILLARS else []


def _detect_tang_hwa(saju: Saju) -> list[SinsalLocation]:
    targets = {JiJi.IN, JiJi.O, JiJi.CHUK}
    return [SinsalLocation.DAY_BRANCH] if saju.day_pillar.ji_ji in targets else []


def _detect_sang_mun(saju: Saju) -> list[SinsalLocation]:
    target = JiJi.by_index(saju.year_pillar.ji_ji.index + 2)
    return _branches_matching(saju, [target])


def _detect_jo_gaek(saju: Saju) -> list[SinsalLocation]:
    target = JiJi.by_index(saju.year_pillar.ji_ji.index - 2 + 12)
    return _branches_matching(saju, [target])


def _detect_gyeok_gak(saju: Saju) -> list[SinsalLocation]:
    if saju.hour_pillar is None:
        return []
    diff = abs(saju.hour_pillar.ji_ji.index - saju.day_pillar.ji_ji.index)
    shortest = 12 - diff if diff > 6 else diff
    if shortest == 2:
        return [SinsalLocation.DAY_BRANCH, SinsalLocation.HOUR_BRANCH]
    return []


def _detect_hyo_sin(saju: Saju) -> list[SinsalLocation]:
    shipsin = ShipsinCalculator.for_cheon_gan(saju.day_stem, saju.day_pillar.ji_ji.bongi)
    return [SinsalLocation.DAY_BRANCH] if shipsin is Shipsin.PYEONIN else []


def _go_sin_target_for(year_branch: JiJi) -> JiJi:
    if year_branch in (JiJi.IN, JiJi.MYO, JiJi.JIN):
        return JiJi.SA
    if year_branch in (JiJi.SA, JiJi.O, JiJi.MI):
        return JiJi.SIN
    if year_branch in (JiJi.SIN, JiJi.YU, JiJi.SUL):
        return JiJi.HAE
    return JiJi.IN  # 亥子丑


def _detect_go_sin(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_go_sin_target_for(saju.year_pillar.ji_ji)])


def _gwa_suk_target_for(year_branch: JiJi) -> JiJi:
    if year_branch in (JiJi.IN, JiJi.MYO, JiJi.JIN):
        return JiJi.CHUK
    if year_branch in (JiJi.SA, JiJi.O, JiJi.MI):
        return JiJi.JIN
    if year_branch in (JiJi.SIN, JiJi.YU, JiJi.SUL):
        return JiJi.MI
    return JiJi.SUL  # 亥子丑


def _detect_gwa_suk(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_gwa_suk_target_for(saju.year_pillar.ji_ji)])


def _detect_cheon_ra_ji_mang(saju: Saju) -> list[SinsalLocation]:
    branches: dict[JiJi, SinsalLocation] = {
        saju.year_pillar.ji_ji: SinsalLocation.YEAR_BRANCH,
        saju.month_pillar.ji_ji: SinsalLocation.MONTH_BRANCH,
        saju.day_pillar.ji_ji: SinsalLocation.DAY_BRANCH,
    }
    if saju.hour_pillar is not None:
        branches[saju.hour_pillar.ji_ji] = SinsalLocation.HOUR_BRANCH
    result: list[SinsalLocation] = []
    if JiJi.SUL in branches and JiJi.HAE in branches:
        result.append(branches[JiJi.SUL])
        result.append(branches[JiJi.HAE])
    if JiJi.JIN in branches and JiJi.SA in branches:
        result.append(branches[JiJi.JIN])
        result.append(branches[JiJi.SA])
    return result


def _detect_nak_jeong(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, [_NAK_JEONG_TARGETS[saju.day_stem]])


def _geup_gak_targets_for(month_branch: JiJi) -> tuple[JiJi, ...]:
    if month_branch in (JiJi.IN, JiJi.MYO, JiJi.JIN):
        return (JiJi.HAE, JiJi.JA)
    if month_branch in (JiJi.SA, JiJi.O, JiJi.MI):
        return (JiJi.MYO, JiJi.MI)
    if month_branch in (JiJi.SIN, JiJi.YU, JiJi.SUL):
        return (JiJi.IN, JiJi.SUL)
    return (JiJi.CHUK, JiJi.JIN)  # 亥子丑


def _detect_geup_gak(saju: Saju) -> list[SinsalLocation]:
    return _branches_matching(saju, _geup_gak_targets_for(saju.month_pillar.ji_ji))


def _detect_cheol_sa_gye(saju: Saju) -> list[SinsalLocation]:
    return [SinsalLocation.DAY_BRANCH] if saju.day_pillar.ji_ji is JiJi.SA else []


_DETECTORS: dict[Sinsal, "callable"] = {  # type: ignore[type-arg]
    Sinsal.CHEON_EUL_GWIIN: _detect_cheon_eul,
    Sinsal.MUN_CHANG_GWIIN: _detect_mun_chang,
    Sinsal.AM_ROK: _detect_am_rok,
    Sinsal.GEUM_YEO: _detect_geum_yeo,
    Sinsal.CHEON_JU_GWIIN: _detect_cheon_ju,
    Sinsal.HAK_DANG_GWIIN: _detect_hak_dang,
    Sinsal.MUN_GOK_GWIIN: _detect_mun_gok,
    Sinsal.TAE_GEUK_GWIIN: _detect_tae_geuk,
    Sinsal.BOK_SIN: _detect_bok_sin,
    Sinsal.CHEON_EUI_SEONG: _detect_cheon_eui,
    Sinsal.BAEKHO_DAE_SAL: _detect_baekho_dae,
    Sinsal.GOEGANG_SAL: _detect_goegang,
    Sinsal.YANG_IN_SAL: _detect_yang_in,
    Sinsal.WONJIN_SAL: _detect_wonjin,
    Sinsal.GWIMUN_GWAN_SAL: _detect_gwimun_gwan,
    Sinsal.HYEON_CHIM: _detect_hyeon_chim,
    Sinsal.HONG_YEOM_SAL: _detect_hong_yeom,
    Sinsal.GO_RAN_SAL: _detect_go_ran,
    Sinsal.TANG_HWA_SAL: _detect_tang_hwa,
    Sinsal.SANG_MUN_SAL: _detect_sang_mun,
    Sinsal.JO_GAEK_SAL: _detect_jo_gaek,
    Sinsal.GYEOK_GAK: _detect_gyeok_gak,
    Sinsal.HYO_SIN_SAL: _detect_hyo_sin,
    Sinsal.GO_SIN_SAL: _detect_go_sin,
    Sinsal.GWA_SUK_SAL: _detect_gwa_suk,
    Sinsal.CHEON_RA_JI_MANG: _detect_cheon_ra_ji_mang,
    Sinsal.NAK_JEONG_GWAN_SAL: _detect_nak_jeong,
    Sinsal.GEUP_GAK_SAL: _detect_geup_gak,
    Sinsal.CHEOL_SA_GYE: _detect_cheol_sa_gye,
}


class SinsalCalculator:
    """신살 검출 — 사주 4기둥에서 길신·흉신 모두 산출."""

    @staticmethod
    def detect(saju: Saju) -> list[SinsalDetection]:
        results: list[SinsalDetection] = []
        for sinsal, detector in _DETECTORS.items():
            locs = detector(saju)
            if locs:
                results.append(SinsalDetection(sinsal=sinsal, locations=tuple(locs)))
        return results
