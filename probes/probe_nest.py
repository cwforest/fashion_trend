# -*- coding: utf-8 -*-
"""포함 관계 탐침 — 상위 키워드가 하위 조합어를 품는가?

A. 검색광고 월간 검색수:  vol(가디건) < Σ vol(…가디건) 이면 포함 아님 (완전일치)
B. 쇼핑인사이트 주간지수: ratio(가디건) < Σ ratio(자식) 인 주가 있으면 포함 아님
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\lim\Desktop\claude_project\fashion_trend")
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from fashion_trend.searchad import get_keywords
from fashion_trend.naver import get_trend

pd.set_option("display.width", 200)
ENV = str(ROOT / ".env")

HEAD = "가디건"

# ══════════════ A. 검색광고 ══════════════
print("=" * 70)
print("A. 검색광고 — 월간 검색수 절대값")
print("=" * 70)

ad = get_keywords([HEAD], env_path=ENV)
ad["total"] = ad[["pc", "mobile"]].sum(axis=1, min_count=1)
norm = ad["keyword"].str.replace(" ", "", regex=False)

self_row = ad[norm == HEAD]
children = ad[(norm != HEAD) & norm.str.endswith(HEAD)]   # '…가디건' 으로 끝나는 것
contains = ad[(norm != HEAD) & norm.str.contains(HEAD)]   # '가디건' 을 포함하는 모든 것

v_self = float(self_row["total"].iloc[0]) if len(self_row) else float("nan")
v_tail = children["total"].sum()
v_all = contains["total"].sum()

print(f"연관어 {len(ad)}개 수신")
print(f"  '{HEAD}' 자체            {v_self:>12,.0f}")
print(f"  '…{HEAD}' 로 끝나는 {len(children):>4}개  {v_tail:>12,.0f}")
print(f"  '{HEAD}' 포함 {len(contains):>4}개        {v_all:>12,.0f}")
print()
print(f"  자체 ÷ 끝나는것합 = {v_self / v_tail:.2f}" if v_tail else "")
print(f"  자체 ÷ 포함전체합 = {v_self / v_all:.2f}" if v_all else "")
print()
print("  상위 10개 자식:")
print(children.nlargest(10, "total")[["keyword", "total"]].to_string(index=False))

# ══════════════ B. 쇼핑인사이트 ══════════════
print()
print("=" * 70)
print("B. 쇼핑인사이트 — 같은 배치 안에서 부모 vs 자식들")
print("=" * 70)

KIDS = children.nlargest(4, "total")["keyword"].tolist()
BATCH = [HEAD] + KIDS
print("배치:", BATCH)

df = get_trend(BATCH, weeks=52, env_path=ENV)
w = df.pivot_table(index="period", columns="keyword", values="ratio")
w = w.reindex(columns=[k for k in BATCH if k in w.columns])

kid_cols = [c for c in w.columns if c != HEAD]
w["자식합"] = w[kid_cols].sum(axis=1, min_count=1)
w["부모-자식합"] = w[HEAD] - w["자식합"]

print()
print(w.tail(12).round(3).to_string())
print()
viol = (w["부모-자식합"] < 0).sum()
n = w["부모-자식합"].notna().sum()
print(f"  자식합이 부모를 넘은 주: {viol} / {n}")
print(f"  부모 ÷ 자식합  중앙값 {(w[HEAD] / w['자식합']).median():.2f}"
      f"  최소 {(w[HEAD] / w['자식합']).min():.2f}")
print()
if viol > 0:
    print("  → 포함 관계 아님 (완전일치에 가깝다)")
else:
    print("  → 포함 관계와 모순 없음 (자식 4개만 본 것이므로 상한은 아니다)")
