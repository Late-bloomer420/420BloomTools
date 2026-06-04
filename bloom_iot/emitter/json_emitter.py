from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import IO, TYPE_CHECKING

from bloom_iot.emitter.base import AbstractEmitter

if TYPE_CHECKING:
    from bloom_iot.adapter.models import SensorReading


class JsonEmitter(AbstractEmitter):
    """Writes newline-delimited JSON — one SensorReading per line."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path) if path else None
        self._file: IO[str] | None = None

    def __enter__(self) -> JsonEmitter:
        if self._path:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._file = open(self._path, "a", encoding="utf-8")
        return self

    def __exit__(self, *_) -> None:
        if self._file:
            self._file.close()
            self._file = None

    def emit(self, reading: SensorReading) -> None:
        line = json.dumps(reading.model_dump(mode="json")) + "\n"
        if self._file:
            self._file.write(line)
            self._file.flush()
        else:
            sys.stdout.write(line)
            sys.stdout.flush()
