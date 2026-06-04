from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SensorReading(BaseModel):
    model_config = ConfigDict(frozen=True)

    sensor_name: str
    sensor_type: str
    raw_value: float
    normalized_value: float
    unit: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    alert_level: Literal["ok", "warn", "critical"] = "ok"
    metadata: dict[str, Any] = Field(default_factory=dict)
