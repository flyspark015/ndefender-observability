"""HTTP utilities for auth and rate limiting."""

from __future__ import annotations

import time
from collections import deque

from fastapi import Request


class RateLimiter:
    def __init__(self, max_requests: int, window_s: int) -> None:
        self.max_requests = max_requests
        self.window_s = window_s
        self._events: dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        bucket = self._events.setdefault(key, deque())
        while bucket and now - bucket[0] > self.window_s:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True


def get_client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    if client is None:
        return "unknown"
    return client.host
