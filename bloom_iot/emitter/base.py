from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bloom_iot.adapter.models import SensorReading


class AbstractEmitter(ABC):
    @abstractmethod
    def emit(self, reading: SensorReading) -> None: ...

    def __enter__(self) -> AbstractEmitter:
        return self

    def __exit__(self, *_) -> None:
        pass
