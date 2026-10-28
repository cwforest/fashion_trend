"""네이버 검색광고 키워드도구 → DataFrame.

쇼핑인사이트(API HUB)와 완전히 별개 체계다. 인증이 HMAC-SHA256 서명이다.

    from fashion_trend.searchad import get_keywords

    df = get_keywords(["가디건", "니트"])

돌려주는 것은 **월간 검색수 절대값**이다. 쇼핑인사이트의 상대지수와 달리
요청이 달라도 숫자를 그대로 비교할 수 있다. 대신 시계열이 없다 — 최근 30일 집계 한 줄뿐.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
from pathlib import Path
from typing import Sequence

import httpx
import pandas as pd

from ._retry import request_with_retry

__all__ = ["get_keywords", "BASE", "MAX_HINTS"]

BASE = "https://api.searchad.naver.com"
PATH = "/keywordstool"
MAX_HINTS = 5          # 힌트 키워드 제한 (쇼핑인사이트와 같은 수치지만 별개 제약)


def _creds(env_path: str | Path = ".env") -> tuple[str, str, str]:
    env = {}
    for line in Path(env_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    missing = [k for k in ("NAVER_AD_CUSTOMER_ID", "NAVER_AD_API_KEY", "NAVER_AD_SECRET_KEY")
               if not env.get(k)]
    if missing:
        raise ValueError(f".env 의 {', '.join(missing)} 가 비어 있다.")
    return env["NAVER_AD_CUSTOMER_ID"], env["NAVER_AD_API_KEY"], env["NAVER_AD_SECRET_KEY"]


def _headers(method: str, path: str, customer: str, api_key: str, secret: str) -> dict:
    """요청마다 서명을 만든다. 서명 원문은 '타임스탬프.메서드.경로' 다."""
    ts = str(round(time.time() * 1000))
    msg = f"{ts}.{method}.{path}"
    sig = base64.b64encode(
        hmac.new(secret.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")
    return {
        "X-Timestamp": ts,
        "X-API-KEY": api_key,
        "X-Customer": customer,
        "X-Signature": sig,
        "Content-Type": "application/json; charset=UTF-8",
    }


def _num(v):
    """'< 10' 은 숫자가 아니다. 가려진 값은 NaN 으로 두고 masked 플래그로 표시한다."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.replace(",", "").strip()
        if s.startswith("<"):
            return float("nan")
        try:
            return float(s)
        except ValueError:
            return float("nan")
    return float("nan")


def get_keywords(
    hints: Sequence[str],
    *,
    show_detail: bool = True,
    env_path: str | Path = ".env",
    timeout: float = 30.0,
) -> pd.DataFrame:
    """힌트 키워드의 연관어와 월간 검색수를 받는다.

    hints 가 5개를 넘으면 나눠 호출한 뒤 합친다(중복 연관어는 제거).

    열: keyword · pc · mobile · total · comp · masked · hint
      pc / mobile  월간 검색수. 10 미만이면 네이버가 '< 10' 으로 가리므로 NaN
      masked       가려진 값이 있었는지 — 소규모 키워드 판단에 꼭 필요하다
      comp         광고 경쟁 정도 (높음/중간/낮음)
    """
    customer, api_key, secret = _creds(env_path)
    names = list(dict.fromkeys(hints))
    frames = []

    for i in range(0, len(names), MAX_HINTS):
        chunk = names[i:i + MAX_HINTS]
        params = {
            "hintKeywords": ",".join(chunk),
            "showDetail": "1" if show_detail else "0",
        }
        # 서명에 타임스탬프가 들어가므로 재시도마다 헤더를 새로 만든다
        r = request_with_retry(
            lambda: httpx.get(BASE + PATH, params=params, timeout=timeout,
                              headers=_headers("GET", PATH, customer, api_key, secret)),
            on_retry=lambda n, why: print(f"  재시도 {n} — {why}"),
        )
        r.raise_for_status()
        for row in r.json().get("keywordList", []):
            pc, mo = row.get("monthlyPcQcCnt"), row.get("monthlyMobileQcCnt")
            frames.append({
                "keyword": row.get("relKeyword"),
                "pc": _num(pc),
                "mobile": _num(mo),
                "comp": row.get("compIdx"),
                "masked": any(isinstance(v, str) and v.strip().startswith("<")
                              for v in (pc, mo)),
                "hint": ",".join(chunk),
            })

    df = pd.DataFrame(frames,
                      columns=["keyword", "pc", "mobile", "comp", "masked", "hint"])
    if df.empty:
        return df
    df["total"] = df["pc"].fillna(0) + df["mobile"].fillna(0)
    df = (df.drop_duplicates(subset="keyword")
            .sort_values("total", ascending=False, ignore_index=True))
    return df[["keyword", "pc", "mobile", "total", "comp", "masked", "hint"]]
