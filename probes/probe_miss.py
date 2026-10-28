# -*- coding: utf-8 -*-
"""결측이 실제로 얼마나 나는가 — 월간 검색수 밴드별 관측률·바닥률.

격자 깊이 상한과 규모 필터 하한을 정하는 근거를 만든다.
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\lim\Desktop\claude_project\fashion_trend")
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import pandas as pd
from fashion_trend.searchad import get_keywords
from fashion_trend.naver import get_trend

pd.set_option("display.width", 220)
ENV = str(ROOT / ".env")
HEAD, ANCHOR, WEEKS, FLOOR = "가디건", "원피스", 104, 0.00437

ad = get_keywords([HEAD], env_path=ENV)
ad["vol"] = ad[["pc", "mobile"]].sum(axis=1, min_count=1)
ad["norm"] = ad["keyword"].str.replace(" ", "", regex=False)
kids = ad[(ad["norm"] != HEAD) & ad["norm"].str.endswith(HEAD)].dropna(subset=["vol"])
# 타깃 밖(남성) 제외
kids = kids[~kids["norm"].str.contains("남자|남성|아동|유아|도매|중고")]

BANDS = [(50, 150), (150, 400), (400, 1200), (1200, 4000), (4000, 15000)]
pick = []
for lo, hi in BANDS:
    sub = kids[(kids["vol"] >= lo) & (kids["vol"] < hi)]
    for _, r in sub.nlargest(3, "vol").iterrows():
        pick.append((f"{lo:,}~{hi:,}", r["norm"], r["vol"]))

print(f"연관어 {len(ad)} 중 타깃 자식 {len(kids)}개 · 표본 {len(pick)}개\n")

rows = []
for i in range(0, len(pick), 4):
    chunk = pick[i:i + 4]
    keys = [ANCHOR] + [k for _, k, _ in chunk]
    df = get_trend(keys, weeks=WEEKS, env_path=ENV)
    w = df.pivot_table(index="period", columns="keyword", values="ratio")
    n_period = len(w)
    for band, k, vol in chunk:
        if k not in w.columns:
            rows.append((band, k, vol, 0.0, np.nan, np.nan)); continue
        s = w[k]
        obs = s.notna().sum()
        at_floor = (s <= FLOOR * 1.01).sum()
        rows.append((band, k, vol, obs / n_period,
                     at_floor / max(obs, 1), s.dropna().nunique() / max(obs, 1)))

res = pd.DataFrame(rows, columns=["밴드", "키워드", "월검색수", "관측률", "바닥률", "고유값비"])
print(res.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print("\n밴드별 요약 (주 수:", n_period, ")")
g = res.groupby("밴드", sort=False).agg(
    n=("키워드", "size"), 월검색수=("월검색수", "median"),
    관측률=("관측률", "mean"), 바닥률=("바닥률", "mean"), 고유값비=("고유값비", "mean"))
print(g.to_string(float_format=lambda x: f"{x:.2f}"))
