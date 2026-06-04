import pytest

from bloom_iot.config import BrokerConfig, SensorConfig, ThresholdConfig


@pytest.fixture
def temp_sensor_config():
    return SensorConfig(
        name="test_temp",
        sensor_type="temperature",
        mqtt_topic="test/temp",
        unit="celsius",
        min_valid=-10.0,
        max_valid=60.0,
        thresholds=ThresholdConfig(
            warn_low=15.0,
            warn_high=30.0,
            crit_low=5.0,
            crit_high=40.0,
        ),
    )


@pytest.fixture
def humidity_sensor_config():
    return SensorConfig(
        name="test_humidity",
        sensor_type="humidity",
        mqtt_topic="test/humidity",
        unit="percent",
        min_valid=0.0,
        max_valid=100.0,
    )


@pytest.fixture
def broker_config():
    return BrokerConfig(host="localhost", port=1883)
