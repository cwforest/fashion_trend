"""트렌드 탐지 지표 — 설계서 §5.

`get_trend` 가 준 DataFrame 을 받아 키워드별 지표와 점수, 생애주기를 낸다.

    from fashion_trend.naver import get_trend
    from fashion_trend.detect import detect

    df = get_trend(["가디건", "니트", "청바지"], weeks=78, gender="f", ages=["10", "20"])
    detect(df)

설계서를 따르되 지금 구현할 수 없는 것은 뺐다.
  · 인구통계 스큐 — 세그먼트별로 따로 조회해야 한다
  · 교차 소스 확인 — 검색어트렌드·문서검색이 아직 없다
  · STL 분해 — statsmodels 미설치. 전년 동기 대비로 대신한다

결측 처리 원칙 (설계서 §2-1): 네이버가 안 보낸 구간은 **0으로 채우지 않는다.**
평균을 낼 때 제외하고, 몇 주가 관측됐는지를 `n_obs` 로 같이 낸다.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["to_matrix", "metrics", "add_score", "classify", "detect", "WEIGHTS"]

# 설계서 §5-2: 임의로 정한 가중치다. 백테스트 전까지 최종값으로 쓰지 않는다.
WEIGHTS = {"growth": 0.4, "accel": 0.3, "persistence": 0.3}


def to_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """긴 형태 → 행=주, 열=키워드. 빠진 주는 NaN 으로 남긴다(0 아님)."""
    m = df.pivot_table(index="period", columns="keyword", values="ratio").sort_index()
    if len(m) > 1:
        step = pd.Series(m.index).diff().dropna().mode()
        if not step.empty:  # 빠진 주가 드러나도록 눈금을 균일하게 채운다
            m = m.reindex(pd.date_range(m.index.min(), m.index.max(), freq=step.iloc[0]))
    m.index.name = "period"
    return m


def _growth(s: pd.Series, w: int) -> float:
    """최근 w주 평균 ÷ 직전 w주 평균 − 1."""
    recent, prior = s.iloc[-w:].mean(), s.iloc[-2 * w:-w].mean()
    if not np.isfinite(recent) or not np.isfinite(prior) or prior == 0:
        return np.nan
    return recent / prior - 1


def _acceleration(s: pd.Series, w: int) -> float:
    """상승률의 변화. 직전 구간 상승률과 그 앞 구간 상승률의 차."""
    now, before = _growth(s, w), _growth(s.iloc[:-w], w)
    if not np.isfinite(now) or not np.isfinite(before):
        return np.nan
    return now - before


def _persistence(s: pd.Series, w: int) -> float:
    """최근 w주 중 전주 대비 오른 주의 비율. 일회성 급등을 거른다."""
    d = s.iloc[-(w + 1):].diff().dropna()
    return float((d > 0).mean()) if len(d) else np.nan


def _novelty(s: pd.Series, w: int) -> float:
    """최근 수준이 장기 평균의 몇 배인가. 처음 보는 수준일수록 크다."""
    recent, long_run = s.iloc[-w:].mean(), s.iloc[:-w].mean()
    if not np.isfinite(recent) or not np.isfinite(long_run) or long_run == 0:
        return np.nan
    return recent / long_run - 1


def _yoy(s: pd.Series, w: int, period: int = 52) -> float:
    """전년 동기 대비. 계절 반복과 진짜 상승을 가른다. 1년치가 없으면 NaN."""
    if len(s) < period + w:
        return np.nan
    recent = s.iloc[-w:].mean()
    year_ago = s.iloc[-(period + w):-period].mean()
    if not np.isfinite(recent) or not np.isfinite(year_ago) or year_ago == 0:
        return np.nan
    return recent / year_ago - 1


def _snr(s: pd.Series, w: int) -> float:
    """신호 대 잡음비 — 상승폭이 그 키워드의 평소 변동성에 비해 큰가 (설계서 §5-4)."""
    hist = s.iloc[:-w].dropna()
    if len(hist) < 3:
        return np.nan
    sd = hist.std()
    if not np.isfinite(sd) or sd == 0:
        return np.nan
    return (s.iloc[-w:].mean() - hist.mean()) / sd


def metrics(df: pd.DataFrame, *, window: int = 4, floor: float = 0.00437) -> pd.DataFrame:
    """키워드별 지표표.

    window : 비교 구간 길이(주). 최근 window 주 vs 직전 window 주.
    floor  : 쇼핑인사이트 양자화 바닥. 이 아래면 해상도를 잃어 지표를 믿을 수 없다.
    """
    m = to_matrix(df)
    rows = []
    for k in m.columns:
        s = m[k]
        obs = s.dropna()
        level = s.iloc[-window:].mean()
        rows.append({
            "keyword": k,
            "level": level,
            "growth": _growth(s, window),
            "accel": _acceleration(s, window),
            "persistence": _persistence(s, window),
            "novelty": _novelty(s, window),
            "yoy": _yoy(s, window),
            "snr": _snr(s, window),
            "n_obs": int(obs.size),
            "n_missing": int(s.isna().sum()),
            # 믿을 수 있는 수치인가 — 설계서 §2-1 의 두 제약
            "at_floor": bool(np.isfinite(level) and level <= floor * 3),
            "sparse": bool(s.isna().mean() > 0.3),
        })
    out = pd.DataFrame(rows).set_index("keyword")
    out.attrs["window"] = window
    out.attrs["asof"] = m.index.max()
    return out


def _z(s: pd.Series) -> pd.Series:
    valid = s.dropna()
    if len(valid) < 2 or valid.std() == 0:
        return pd.Series(0.0, index=s.index).where(s.notna())
    return (s - valid.mean()) / valid.std()


def add_score(mx: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.DataFrame:
    """Z 표준화 후 가중합 (설계서 §5-2).

    가중치는 임의값이다. 백테스트로 조정하기 전까지 순위를 그대로 믿지 않는다.
    """
    w = weights or WEIGHTS
    out = mx.copy()
    for col in w:
        out[f"z_{col}"] = _z(out[col])
    out["score"] = sum(out[f"z_{c}"].fillna(0) * v for c, v in w.items())
    out.loc[out[list(w)].isna().all(axis=1), "score"] = np.nan
    return out.sort_values("score", ascending=False)


def classify(mx: pd.DataFrame, *, level_q: float = 0.6,
             grow: float = 0.10, persist: float = 0.5) -> pd.DataFrame:
    """생애주기 분류 (설계서 §5-3)."""
    out = mx.copy()
    cutoff = out["level"].quantile(level_q)

    def stage(r) -> str:
        if not np.isfinite(r.get("growth", np.nan)):
            return "Unknown"
        high = np.isfinite(r["level"]) and r["level"] >= cutoff
        rising = r["growth"] >= grow and (r.get("persistence") or 0) >= persist
        if r["growth"] <= -grow:
            return "Declining"
        if rising:
            return "Growing" if high else "Emerging"
        return "Mature" if high else "Flat"

    out["stage"] = out.apply(stage, axis=1)
    # 설계서 §5-5: 하락 경보를 상승 추천과 동등하게 다룬다
    out["direction"] = np.where(out["stage"] == "Declining", "stop",
                         np.where(out["stage"].isin(["Emerging", "Growing"]), "watch", "hold"))
    return out


def detect(df: pd.DataFrame, *, window: int = 4,
           weights: dict[str, float] | None = None) -> pd.DataFrame:
    """지표 → 점수 → 생애주기까지 한 번에."""
    return classify(add_score(metrics(df, window=window), weights))
