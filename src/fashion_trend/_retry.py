"""요청 재시도 — 네트워크가 한 번 끊겼다고 수집 전체가 날아가지 않게.

DNS 실패·타임아웃·연결 끊김과 429/5xx 만 다시 시도한다.
4xx(키가 틀렸거나 파라미터가 잘못된 경우)는 다시 해도 같으므로 즉시 올린다.
"""

from __future__ import annotations

import time
from typing import Callable

import httpx

__all__ = ["request_with_retry", "RETRYABLE_STATUS"]

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


def request_with_retry(
    send: Callable[[], httpx.Response],
    *,
    retries: int = 4,
    backoff: float = 1.0,
    max_backoff: float = 16.0,
    on_retry: Callable[[int, str], None] | None = None,
) -> httpx.Response:
    """send() 를 성공할 때까지 다시 부른다. 마지막 시도도 실패하면 예외를 그대로 올린다."""
    delay = backoff
    last_exc: Exception | None = None

    for attempt in range(1, retries + 1):
        reason = ""
        try:
            r = send()
            if r.status_code not in RETRYABLE_STATUS:
                return r                      # 성공이든 4xx 든 그대로 돌려준다
            reason = f"HTTP {r.status_code}"
            last_exc = httpx.HTTPStatusError(reason, request=r.request, response=r)
        except httpx.TransportError as e:     # ConnectError·ReadTimeout·DNS 실패 등
            reason = f"{type(e).__name__}: {e}"
            last_exc = e

        if attempt == retries:
            break
        if on_retry:
            on_retry(attempt, reason)
        time.sleep(delay)
        delay = min(delay * 2, max_backoff)

    assert last_exc is not None
    raise last_exc
