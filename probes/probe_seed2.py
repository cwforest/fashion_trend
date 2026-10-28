# -*- coding: utf-8 -*-
"""시드 후보 재평가 — 힌트 1개씩 단독 조회 (묶음 왜곡 제거)."""
import sys, re, json
from pathlib import Path
ROOT = Path(r"C:\Users\lim\Desktop\claude_project\fashion_trend")
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from fashion_trend.searchad import get_keywords
ENV = str(ROOT / ".env")
BAD = re.compile("중고|대여|도매|사입|쿠폰|무료배송|남성|남자|아동|유아|키즈|빅사이즈")
LO, HI = 100, 10000

CURRENT = ["블라우스","셔츠","니트","가디건","티셔츠","맨투맨","후드티","크롭티","베스트",
           "청바지","슬랙스","와이드팬츠","카고팬츠","레깅스","미니스커트","롱스커트",
           "원피스","점프수트","셋업","자켓","블레이저","코트","트렌치코트","패딩",
           "무스탕","바람막이"]
CAND = ["스커트","팬츠","바지","나시","반바지","집업","점퍼","니트원피스","플리스","조끼"]

rows, store = [], {}
for s in CURRENT + CAND:
    ad = get_keywords([s], env_path=ENV)
    ad["vol"] = ad[["pc","mobile"]].sum(axis=1, min_count=1)
    ad["norm"] = ad["keyword"].str.replace(" ", "", regex=False)
    own = ad.loc[ad["norm"] == s, "vol"]
    kids = ad[(ad["norm"] != s) & ad["norm"].str.endswith(s)].dropna(subset=["vol"])
    kids = kids[~kids["norm"].str.contains(BAD)]
    keep = kids[(kids["vol"] >= LO) & (kids["vol"] < HI)]
    store[s] = keep["norm"].tolist()
    rows.append((s, "현행" if s in CURRENT else "후보",
                 float(own.iloc[0]) if len(own) else float("nan"),
                 len(ad), len(kids), len(keep)))
    print(f"  {s:6} {len(keep):>4}")

df = pd.DataFrame(rows, columns=["시드","구분","자기검색량","연관어","타깃자식","수확"])
df.to_csv("seed_eval.csv", index=False, encoding="utf-8-sig")
json.dump(store, open("seed_children.json","w",encoding="utf-8"), ensure_ascii=False)

print()
for g in ["현행","후보"]:
    d = df[df["구분"]==g].sort_values("수확", ascending=False)
    print(f"───── {g} ─────")
    print(d[["시드","자기검색량","연관어","타깃자식","수확"]].to_string(
        index=False, formatters={"자기검색량": lambda v: f"{v:,.0f}" if v==v else "—"}))
    print()

uniq = set()
for s in CURRENT:
    uniq |= set(store[s])
print(f"현행 26개 수확 합계 {df[df.구분=='현행']['수확'].sum():,}  (중복 제거 {len(uniq):,})")
