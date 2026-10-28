# -*- coding: utf-8 -*-
"""쇼핑인사이트(= 시계열을 실제로 뽑는 소스) 단독 재확인.

C. 부모 vs 자식 — 자식 수를 늘려 가며 (앵커 없이 한 배치 안에서만 비교하므로 유효)
D. 수식어 순서를 가리는가 — 니트가디건 vs 가디건니트
E. 띄어쓰기는 정말 무시되는가 (대조군)
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\lim\Desktop\claude_project\fashion_trend")
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from fashion_trend.naver import get_trend

pd.set_option("display.width", 220)
ENV = str(ROOT / ".env")
W = 52


def pull(keys, label):
    df = get_trend(keys, weeks=W, env_path=ENV)
    w = df.pivot_table(index="period", columns="keyword", values="ratio")
    return w.reindex(columns=[k for k in keys if k in w.columns])


print("=" * 72)
print("C. 부모 vs 자식 — 배치를 나눠 자식을 12개까지")
print("=" * 72)

HEAD = "가디건"
KIDS = ["여성가디건", "남자가디건", "니트가디건", "유니클로가디건",
        "남성가디건", "캐시미어가디건", "아가일가디건", "레이어드가디건",
        "버건디가디건", "여자가디건", "크롭가디건", "루즈핏가디건"]

# 배치마다 부모를 끼워 같은 분모로 맞춘다 (앵커 체이닝과 같은 원리)
parts = []
for i in range(0, len(KIDS), 4):
    chunk = KIDS[i:i + 4]
    w = pull([HEAD] + chunk, f"batch{i}")
    scale = w[HEAD].mean()
    parts.append(w[[c for c in w.columns if c != HEAD]] / scale)
    print(f"  배치 {i//4 + 1}: {chunk}  (부모평균 {scale:.3f} 로 정규화)")

kids = pd.concat(parts, axis=1)
base = pull([HEAD], "solo")
par = base[HEAD] / base[HEAD].mean()          # 부모도 자기 평균=1 로

tbl = pd.DataFrame({"부모": par, "자식합": kids.sum(axis=1, min_count=1)})
tbl["비율"] = tbl["부모"] / tbl["자식합"]

print()
print(tbl.tail(10).round(3).to_string())
print()
print(f"  자식 {kids.shape[1]}개 · 주 {len(tbl)}")
print(f"  자식합 > 부모 인 주: {(tbl['부모'] < tbl['자식합']).sum()} / {tbl['비율'].notna().sum()}")
print(f"  부모 ÷ 자식합  중앙값 {tbl['비율'].median():.3f}  최대 {tbl['비율'].max():.3f}")

print()
print("=" * 72)
print("D. 수식어 순서를 가리는가")
print("=" * 72)

PAIRS = [("니트가디건", "가디건니트"),
         ("버건디니트가디건", "니트버건디가디건")]
flat = [k for p in PAIRS for k in p]
w = pull(flat, "order")
print()
print(w.tail(8).round(3).to_string())
print()
for a, b in PAIRS:
    if a in w.columns and b in w.columns:
        s = (w[a] - w[b]).abs().sum()
        print(f"  {a:18} vs {b:18}  차이합 {s:.4f}"
              f"   → {'같다 (순서 무시)' if s < 1e-6 else '다르다 (순서 구분)'}")
    else:
        miss = [x for x in (a, b) if x not in w.columns]
        print(f"  {a} vs {b} → 응답에 없음: {miss}")

print()
print("=" * 72)
print("E. 띄어쓰기 대조군")
print("=" * 72)
w = pull(["니트가디건", "니트 가디건"], "space")
print()
print(w.tail(5).round(3).to_string())
if w.shape[1] == 2:
    s = (w.iloc[:, 0] - w.iloc[:, 1]).abs().sum()
    print(f"\n  차이합 {s:.4f} → {'같다 (띄어쓰기 무시)' if s < 1e-6 else '다르다'}")
