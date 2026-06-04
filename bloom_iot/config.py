from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ThresholdConfig(BaseModel):
    warn_low: float | None = None
    warn_high: float | None = None
    crit_low: float | None = None
    crit_high: float | None = None


class SensorConfig(BaseModel):
    name: str
    sensor_type: Literal["temperature", "humidity", "soil_moisture", "light", "generic"]
    mqtt_topic: str
    unit: str
    min_valid: float = -999.0
    max_valid: float = 9999.0
    thresholds: ThresholdConfig | None = None


class BrokerConfig(BaseModel):
    host: str = "localhost"
    port: int = 1883
    keepalive: int = 60
    username: str | None = None
    password: str | None = None
    mqtt_version: Literal["3.1.1", "5.0"] = "3.1.1"


class OutputConfig(BaseModel):
    mode: Literal["dashboard", "json", "both"] = "dashboard"
    json_path: str | None = None


class FrameworkConfig(BaseModel):
    broker: BrokerConfig = Field(default_factory=BrokerConfig)
    sensors: list[SensorConfig]
    output: OutputConfig = Field(default_factory=OutputConfig)
    refresh_rate: float = 2.0


def load_config(path: str | Path) -> FrameworkConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return FrameworkConfig(**data)
