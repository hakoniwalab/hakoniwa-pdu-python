from __future__ import annotations

import threading
from typing import Any


class RpcCallFuture:
    """Lightweight future for one RPC request."""

    def __init__(self, *, service_id: int, client_id: int, request_id: int) -> None:
        self.service_id = service_id
        self.client_id = client_id
        self.request_id = request_id
        self._done = threading.Event()
        self._result: Any = None
        self._exception: BaseException | None = None
        self._lock = threading.Lock()

    def done(self) -> bool:
        return self._done.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        return self._done.wait(timeout)

    def result(self, timeout: float | None = None) -> Any:
        if not self._done.wait(timeout):
            raise TimeoutError()
        if self._exception is not None:
            raise self._exception
        return self._result

    def exception(self, timeout: float | None = None) -> BaseException | None:
        if not self._done.wait(timeout):
            raise TimeoutError()
        return self._exception

    def set_result(self, result: Any) -> None:
        with self._lock:
            if self._done.is_set():
                return
            self._result = result
            self._done.set()

    def set_exception(self, exc: BaseException) -> None:
        with self._lock:
            if self._done.is_set():
                return
            self._exception = exc
            self._done.set()
