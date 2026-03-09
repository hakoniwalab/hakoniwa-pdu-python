from __future__ import annotations

import os
import time


def enabled() -> bool:
    value = os.getenv("HAKO_RPC_PROFILE_PREPARE", "0")
    return value not in ("", "0")


class ScopedTimer:
    def __init__(self, label: str) -> None:
        self.label = label
        self.active = enabled()
        self.start_usec = time.perf_counter_ns() // 1000 if self.active else 0

    def __enter__(self) -> "ScopedTimer":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self.active:
            return
        end_usec = time.perf_counter_ns() // 1000
        elapsed_usec = end_usec - self.start_usec
        print(f"PROFILE_PY: {self.label} usec={elapsed_usec}")

