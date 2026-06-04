from __future__ import annotations

import json
from typing import TYPE_CHECKING

from bloom_iot.adapter.models import SensorReading
from bloom_iot.adapter.thresholds import ThresholdChecker

if TYPE_CHECKING:
    from bloom_iot.config import SensorConfig


_CANONICAL_UNITS: dict[str, str] = {
    "celsius": "°C",
    "fahrenheit": "°C",   # normalized to Celsius
    "percent": "%",
    "lux": "lux",
    "raw": "raw",
}


class DataAdapter:
    """Converts a raw (topic, payload) pair into a normalized SensorReading."""

    def __init__(self, sensors: list[SensorConfig]) -> None:
        self._topic_map: dict[str, SensorConfig] = {s.mqtt_topic: s for s in sensors}

    def adapt(self, topic: str, payload: str | bytes) -> SensorReading | None:
        config = self._topic_map.get(topic)
        if config is None:
            return None

        raw = self._parse_payload(payload)
        if raw is None:
            return None

        if not (config.min_valid <= raw <= config.max_valid):
            return None

        normalized = self._normalize(raw, config)
        alert = ThresholdChecker.check(normalized, config.thresholds)
        canonical_unit = _CANONICAL_UNITS.get(config.unit.lower(), config.unit)

        return SensorReading(
            sensor_name=config.name,
            sensor_type=config.sensor_type,
            raw_value=raw,
            normalized_value=normalized,
            unit=canonical_unit,
            alert_level=alert,
        )

    def _parse_payload(self, payload: str | bytes) -> float | None:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8", errors="ignore")
        payload = payload.strip()

        # Try plain float first (most common from Arduino sketches)
        try:
            return float(payload)
        except ValueError:
            pass

        # Try JSON object with common value keys
        try:
            obj = json.loads(payload)
            if isinstance(obj, (int, float)):
                return float(obj)
            if isinstance(obj, dict):
                for key in ("value", "v", "data", "temperature", "humidity",
                            "soil_moisture", "light", "lux", "moisture"):
                    if key in obj:
                        return float(obj[key])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

        return None

    def _normalize(self, raw: float, config: SensorConfig) -> float:
        unit = config.unit.lower()
        if unit == "fahrenheit":
            return (raw - 32.0) * 5.0 / 9.0
        return raw
