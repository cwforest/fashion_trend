"""쇼핑인사이트 → DataFrame.

    from fashion_trend.naver import get_trend

    df = get_trend(["가디건", "니트"], weeks=52, gender="f", ages=["10", "20"])
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

import httpx
import pandas as pd

from ._retry import request_with_retry

HOST = "https://naverapihub.apigw.ntruss.com"
ENDPOINT = "/shopping/v1/category/keywords"
SEARCH_ENDPOINT = "/search-trend/v1/search"
FASHION = "50000000"          # 패션의류
MAX_KEYWORDS = 5              # 네이버 제한


def _keys(env_path: str | Path = ".env") -> tuple[str, str]:
    env = {}
    for line in Path(env_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env["NAVER_HUB_KEY_ID"], env["NAVER_HUB_KEY"]


def get_trend(
    keywords: Sequence[str],
    *,
    weeks: int = 52,
    start: str | None = None,
    end: str | None = None,
    time_unit: str = "week",
    category: str = FASHION,
    gender: str | None = None,
    ages: Sequence[str] | None = None,
    env_path: str | Path = ".env",
) -> pd.DataFrame:
    """키워드 추이를 받아 DataFrame 으로 돌려준다.

    열: period(날짜) · keyword · ratio · batch

    keywords 가 5개를 넘으면 자동으로 나눠 호출한다.
    ratio 는 **한 요청 안에서** 최댓값을 100으로 둔 상대값이다.
    그래서 batch 가 다르면 ratio 끼리 바로 비교하면 안 된다.
    """
    if start is None or end is None:
        last = date.today() - timedelta(weeks=1)      # 이번 주는 아직 안 끝났다
        start, end = (last - timedelta(weeks=weeks)).isoformat(), last.isoformat()

    names = list(dict.fromkeys(keywords))             # 중복 제거, 순서 유지
    key_id, key = _keys(env_path)
    headers = {
        "X-NCP-APIGW-API-KEY-ID": key_id,
        "X-NCP-APIGW-API-KEY": key,
        "Content-Type": "application/json",
    }

    frames = []
    for b, chunk in enumerate(
        [names[i:i + MAX_KEYWORDS] for i in range(0, len(names), MAX_KEYWORDS)], 1
    ):
        body = {
            "startDate": start, "endDate": end, "timeUnit": time_unit,
            "category": category,
            "keyword": [{"name": n, "param": [n]} for n in chunk],
        }
        if gender:
            body["gender"] = gender
        if ages:
            body["ages"] = list(ages)

        r = request_with_retry(
            lambda: httpx.post(HOST + ENDPOINT, headers=headers, json=body, timeout=30.0),
            on_retry=lambda n, why: print(f"  재시도 {n} — {why}"),
        )
        r.raise_for_status()

        frames += [
            {"period": d["period"], "keyword": res["title"],
             "ratio": float(d["ratio"]), "batch": b}
            for res in r.json().get("results", [])
            for d in res.get("data", [])
        ]

    df = pd.DataFrame(frames, columns=["period", "keyword", "ratio", "batch"])
    if not df.empty:
        df["period"] = pd.to_datetime(df["period"])
        df = df.sort_values(["keyword", "period"], ignore_index=True)
    return df


def to_wide(df: pd.DataFrame) -> pd.DataFrame:
    """행=날짜, 열=키워드 로 펴기. NaN 은 네이버가 보내지 않은 구간이다."""
    return df.pivot_table(index="period", columns="keyword", values="ratio")


# ─── 검색어트렌드 ─────────────────────────────────────────────────────
#
# 쇼핑인사이트와 세 가지가 다르다.
#   1) 한 그룹에 키워드를 최대 20개 넣으면 **합산**해 준다 (쇼핑인사이트는 1개만)
#   2) 연령 코드가 10/20 이 아니라 1~11 구간 코드다
#   3) 카테고리가 없다 — 네이버 전체 검색이라 패션으로 한정할 수 없다

MAX_GROUPS = 5          # 요청당 그룹 수 (실측 확인: 6개면 400)
MAX_IN_GROUP = 20       # 그룹당 키워드 수 (실측 확인: 21개면 400)

# 네이버 연령 구간 코드
AGE_BUCKETS = {
    "1": "0~12", "2": "13~18", "3": "19~24", "4": "25~29", "5": "30~34",
    "6": "35~39", "7": "40~44", "8": "45~49", "9": "50~54", "10": "55~59",
    "11": "60~",
}

# 쇼핑인사이트식 10/20/... 을 위 코드로 옮긴다.
# 구간이 10년 단위로 안 떨어진다 — 19세는 '3'(19~24)에 들어가므로 20대로 샌다.
# 정확히 맞추고 싶으면 ages_raw 로 코드를 직접 넘길 것.
_DECADE_TO_BUCKETS = {
    "10": ["2"], "20": ["3", "4"], "30": ["5", "6"],
    "40": ["7", "8"], "50": ["9", "10"], "60": ["11"],
}


def _to_buckets(ages: Sequence[str]) -> list[str]:
    out: list[str] = []
    for a in ages:
        a = str(a)
        if a in _DECADE_TO_BUCKETS:
            out += _DECADE_TO_BUCKETS[a]
        elif a in AGE_BUCKETS:
            out.append(a)
        else:
            raise ValueError(f"모르는 연령값 {a!r}. 10/20/… 또는 1~11 코드만 된다.")
    return list(dict.fromkeys(out))


def get_search_trend(
    groups,
    *,
    weeks: int = 52,
    start: str | None = None,
    end: str | None = None,
    time_unit: str = "week",
    gender: str | None = None,
    ages: Sequence[str] | None = None,
    ages_raw: Sequence[str] | None = None,
    device: str | None = None,
    env_path: str | Path = ".env",
) -> pd.DataFrame:
    """검색어트렌드 — 검색 관심도 시계열.

    `get_trend` 가 '네이버쇼핑에서 상품을 클릭한 수' 라면 이쪽은 '검색창에 친 수' 다.
    둘을 나란히 놓으면 "검색은 느는데 클릭은 안 는다" 같은 괴리를 볼 수 있다.

    groups : 두 가지 형태를 받는다
        ["가디건", "니트"]                      그대로 각각
        {"가디건": ["가디건", "카디건"]}          표기 변형을 묶어 합산

    ages      쇼핑인사이트와 같은 ["10","20"] 형식. 내부에서 구간 코드로 바꾼다
    ages_raw  네이버 코드("2","3",…)를 직접 쓸 때. 주면 ages 를 무시한다

    열: period · keyword(그룹 이름) · ratio · batch
    """
    if isinstance(groups, dict):
        items = [(name, list(kws)) for name, kws in groups.items()]
    else:
        items = [(k, [k]) for k in dict.fromkeys(groups)]
    for name, kws in items:
        if len(kws) > MAX_IN_GROUP:
            raise ValueError(f"'{name}' 그룹에 키워드가 {len(kws)}개다. {MAX_IN_GROUP}개까지만 된다.")

    if start is None or end is None:
        last = date.today() - timedelta(weeks=1)
        start, end = (last - timedelta(weeks=weeks)).isoformat(), last.isoformat()

    key_id, key = _keys(env_path)
    headers = {
        "X-NCP-APIGW-API-KEY-ID": key_id,
        "X-NCP-APIGW-API-KEY": key,
        "Content-Type": "application/json",
    }

    frames = []
    for b, chunk in enumerate(
        [items[i:i + MAX_GROUPS] for i in range(0, len(items), MAX_GROUPS)], 1
    ):
        body = {
            "startDate": start, "endDate": end, "timeUnit": time_unit,
            "keywordGroups": [{"groupName": n, "keywords": kws} for n, kws in chunk],
        }
        if gender:
            body["gender"] = gender
        if ages_raw:
            body["ages"] = list(ages_raw)
        elif ages:
            body["ages"] = _to_buckets(ages)
        if device:
            body["device"] = device

        r = request_with_retry(
            lambda: httpx.post(HOST + SEARCH_ENDPOINT, headers=headers, json=body,
                               timeout=30.0),
            on_retry=lambda n, why: print(f"  재시도 {n} — {why}"),
        )
        r.raise_for_status()

        frames += [
            {"period": d["period"], "keyword": res["title"],
             "ratio": float(d["ratio"]), "batch": b}
            for res in r.json().get("results", [])
            for d in res.get("data", [])
        ]

    df = pd.DataFrame(frames, columns=["period", "keyword", "ratio", "batch"])
    if not df.empty:
        df["period"] = pd.to_datetime(df["period"])
        df = df.sort_values(["keyword", "period"], ignore_index=True)
    return df


def use_korean_font() -> str | None:
    """matplotlib 에 한글 폰트를 물린다. 안 하면 글자가 네모로 나온다."""
    import matplotlib
    from matplotlib import font_manager

    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("Malgun Gothic", "NanumGothic", "AppleGothic", "Gulim", "NanumBarunGothic"):
        if name in installed:
            matplotlib.rcParams["font.family"] = name
            matplotlib.rcParams["axes.unicode_minus"] = False
            return name
    return None


def plot_trend(
    keywords: Sequence[str],
    *,
    weeks: int = 52,
    start: str | None = None,
    end: str | None = None,
    time_unit: str = "week",
    category: str = FASHION,
    gender: str | None = None,
    ages: Sequence[str] | None = None,
    env_path: str | Path = ".env",
    logy: bool = False,
    title: str | None = None,
    figsize: tuple[float, float] = (11, 4.5),
    ax=None,
):
    """`get_trend` 와 같은 인자를 받아 시계열 그래프까지 그린다.

    돌려주는 값은 (df, ax) — 그림만 봐도 되고, df 를 이어서 써도 된다.

        df, ax = plot_trend(["가디건", "니트"], weeks=52, gender="f", ages=["10", "20"])

    logy : 작은 키워드가 바닥에 깔려 안 보일 때 세로축을 로그로.
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter, StrMethodFormatter

    use_korean_font()

    df = get_trend(keywords, weeks=weeks, start=start, end=end, time_unit=time_unit,
                   category=category, gender=gender, ages=ages, env_path=env_path)
    if df.empty:
        raise ValueError("받은 데이터가 없다. 키워드나 기간을 확인할 것.")

    wide = to_wide(df)
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    wide.plot(ax=ax, linewidth=1.8, logy=logy)

    if title is None:
        seg = []
        if gender:
            seg.append({"f": "여성", "m": "남성"}[gender])
        if ages:
            seg.append("·".join(f"{a}대" for a in ages))
        title = "쇼핑 클릭 추이" + (f" — {' '.join(seg)}" if seg else "")
    ax.set_title(title, fontsize=13, pad=12)

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(axis="y", alpha=0.25, linewidth=0.7)
    ax.grid(axis="x", alpha=0.12, linewidth=0.7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    # 로그축 기본 눈금(10^-2)은 음수기호가 한글 폰트에 없어 깨진다 → 평범한 숫자로
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
    if logy:
        ax.yaxis.set_minor_formatter(NullFormatter())

    # 선 끝에 이름을 붙인다. 선이 한곳으로 모이면 글자가 겹치므로 세로로 밀어 떨어뜨린다.
    if wide.shape[1] <= 7:
        ax.get_legend().remove()
        ends = []
        for line, name in zip(ax.get_lines(), wide.columns):
            ys = wide[name].dropna()
            if ys.empty:
                continue
            frac = ax.transAxes.inverted().transform(
                ax.transData.transform((0, ys.iloc[-1])))[1]
            ends.append([frac, name, line.get_color()])

        gap = 0.075                       # 축 높이 대비 최소 간격
        ends.sort(key=lambda e: e[0])
        for i in range(1, len(ends)):     # 아래에서 위로 밀어 올린다
            if ends[i][0] - ends[i - 1][0] < gap:
                ends[i][0] = ends[i - 1][0] + gap
        overflow = ends[-1][0] - 1.0 if ends else 0
        if overflow > 0:                  # 위로 삐져나가면 전체를 내린다
            for e in ends:
                e[0] -= overflow

        for frac, name, color in ends:
            ax.text(1.015, frac, name, transform=ax.transAxes, va="center",
                    fontsize=10, color=color)
        ax.margins(x=0.02)
    else:
        ax.legend(loc="center left", bbox_to_anchor=(1.015, 0.5), frameon=False, fontsize=9)

    ax.figure.tight_layout()
    return df, ax
