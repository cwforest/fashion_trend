# -*- coding: utf-8 -*-
"""힌트 1개씩 단독 조회 — 묶음 조회의 왜곡 확인."""
import sys, re
from pathlib import Path
ROOT = Path(r"C:\Users\lim\Desktop\claude_project\fashion_trend")
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from fashion_trend.searchad import get_keywords
ENV = str(ROOT / ".env")
BAD = re.compile("중고|대여|도매|사입|쿠폰|무료배송|남성|남자|아동|유아|키즈|빅사이즈")

for s in ["스커트", "팬츠", "셋업", "가디건"]:
    ad = get_keywords([s], env_path=ENV)
    ad["vol"] = ad[["pc","mobile"]].sum(axis=1, min_count=1)
    ad["norm"] = ad["keyword"].str.replace(" ", "", regex=False)
    kids = ad[(ad["norm"] != s) & ad["norm"].str.endswith(s)].dropna(subset=["vol"])
    kids = kids[~kids["norm"].str.contains(BAD)]
    keep = kids[(kids["vol"] >= 100) & (kids["vol"] < 10000)]
    print(f"{s:5} 연관어 {len(ad):>5}  타깃자식 {len(kids):>4}  필터통과 {len(keep):>4}")
    print("        상위:", " · ".join(keep.nlargest(6, "vol")["norm"].tolist()))
