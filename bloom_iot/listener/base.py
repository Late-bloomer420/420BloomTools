from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


class AbstractSensorListener(ABC):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def on_message(self, callback: Callable[[str, str | bytes], None]) -> None:
        """Register a callback invoked as callback(topic, payload) on each message."""
        ...
