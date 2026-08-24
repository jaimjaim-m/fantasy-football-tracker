"""Tiny in-process TTL cache for ESPN league objects."""

from __future__ import annotations

import time
from threading import Lock
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: float) -> None:
        self.ttl_seconds = ttl_seconds
        self._lock = Lock()
        self._store: dict[str, tuple[float, T]] = {}

    def get(self, key: str) -> T | None:
        now = time.monotonic()
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            expires_at, value = item
            if now >= expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: T) -> T:
        with self._lock:
            self._store[key] = (time.monotonic() + self.ttl_seconds, value)
            return value

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
