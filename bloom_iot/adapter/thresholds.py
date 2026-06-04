from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from bloom_iot.config import ThresholdConfig


class ThresholdChecker:
    @staticmethod
    def check(value: float, config: ThresholdConfig | None) -> Literal["ok", "warn", "critical"]:
        if config is None:
            return "ok"
        if (config.crit_low is not None and value < config.crit_low) or \
           (config.crit_high is not None and value > config.crit_high):
            return "critical"
        if (config.warn_low is not None and value < config.warn_low) or \
           (config.warn_high is not None and value > config.warn_high):
            return "warn"
        return "ok"
