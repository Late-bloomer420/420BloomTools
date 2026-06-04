import json

import pytest

from bloom_iot.adapter.normalizer import DataAdapter
from bloom_iot.adapter.thresholds import ThresholdChecker
from bloom_iot.config import SensorConfig, ThresholdConfig


def test_adapt_plain_float(temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    reading = adapter.adapt("test/temp", "22.5")
    assert reading is not None
    assert reading.normalized_value == pytest.approx(22.5)
    assert reading.alert_level == "ok"


def test_adapt_bytes_payload(temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    reading = adapter.adapt("test/temp", b"22.5")
    assert reading is not None
    assert reading.normalized_value == pytest.approx(22.5)


def test_adapt_json_value_key(temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    payload = json.dumps({"value": 22.5})
    reading = adapter.adapt("test/temp", payload)
    assert reading is not None
    assert reading.normalized_value == pytest.approx(22.5)


def test_adapt_json_sensor_type_key(temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    payload = json.dumps({"temperature": 22.5})
    reading = adapter.adapt("test/temp", payload)
    assert reading is not None
    assert reading.normalized_value == pytest.approx(22.5)


def test_adapt_out_of_bounds_returns_none(temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    assert adapter.adapt("test/temp", "999.0") is None  # above max_valid=60


def test_adapt_below_min_valid_returns_none(temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    assert adapter.adapt("test/temp", "-50.0") is None  # below min_valid=-10


def test_adapt_unknown_topic_returns_none(temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    assert adapter.adapt("unknown/topic", "22.5") is None


def test_adapt_invalid_payload_returns_none(temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    assert adapter.adapt("test/temp", "not_a_number") is None


def test_fahrenheit_normalization():
    sensor = SensorConfig(
        name="f_temp",
        sensor_type="temperature",
        mqtt_topic="test/fahr",
        unit="fahrenheit",
        min_valid=0.0,
        max_valid=200.0,
    )
    adapter = DataAdapter([sensor])
    reading = adapter.adapt("test/fahr", "72.0")  # 72°F = 22.22°C
    assert reading is not None
    assert reading.normalized_value == pytest.approx(22.222, abs=0.01)
    assert reading.unit == "°C"


@pytest.mark.parametrize("value,expected", [
    (22.0, "ok"),
    (14.9, "warn"),   # below warn_low=15
    (30.1, "warn"),   # above warn_high=30
    (4.9, "critical"),  # below crit_low=5
    (40.1, "critical"),  # above crit_high=40
])
def test_threshold_levels(value, expected, temp_sensor_config):
    adapter = DataAdapter([temp_sensor_config])
    reading = adapter.adapt("test/temp", str(value))
    assert reading is not None
    assert reading.alert_level == expected


def test_threshold_checker_no_config():
    assert ThresholdChecker.check(100.0, None) == "ok"


def test_threshold_checker_crit_high():
    cfg = ThresholdConfig(crit_high=50.0)
    assert ThresholdChecker.check(51.0, cfg) == "critical"
    assert ThresholdChecker.check(49.0, cfg) == "ok"


def test_threshold_checker_warn_low():
    cfg = ThresholdConfig(warn_low=20.0)
    assert ThresholdChecker.check(19.0, cfg) == "warn"
    assert ThresholdChecker.check(21.0, cfg) == "ok"
