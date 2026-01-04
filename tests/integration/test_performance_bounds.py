from __future__ import annotations

from ambilight.utils.bounded_queue import BoundedQueue


def test_bounded_queue_drops_oldest() -> None:
    queue = BoundedQueue[int](maxlen=3)
    for i in range(10):
        queue.put(i)
    assert queue.size() == 3
    assert queue.get_latest() == 9
