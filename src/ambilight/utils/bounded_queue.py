"""Bounded queue helper with drop-oldest behavior."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Deque, Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class BoundedQueue(Generic[T]):
    """Thread-safe bounded queue that drops the oldest item when full."""

    maxlen: int
    _items: Deque[T] = field(default_factory=deque, init=False)
    _lock: Lock = field(default_factory=Lock, init=False)

    def put(self, item: T) -> None:
        with self._lock:
            if len(self._items) >= self.maxlen:
                self._items.popleft()
            self._items.append(item)

    def get_latest(self) -> Optional[T]:
        with self._lock:
            if not self._items:
                return None
            return self._items[-1]

    def size(self) -> int:
        with self._lock:
            return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
