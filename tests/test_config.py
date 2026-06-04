import textwrap
from pathlib import Path

import pytest
from pydantic import ValidationError

from bloom_iot.config import FrameworkConfig, SensorConfig, load_config


def test_load_example_config(tmp_path):
    example = Path(__file__).parent.parent / "config" / "sensors.example.yaml"
    config = load_config(example)
    assert len(config.sensors) == 4
    assert config.broker.host == "localhost"
    assert config.broker.port == 1883


def test_load_config_defaults(tmp_path):
    yaml_content = textwrap.dedent("""\
        sensors:
          - name: s1
            sensor_type: temperature
            mqtt_topic: test/t
            unit: celsius
    """)
    cfg_file = tmp_path / "sensors.yaml"
    cfg_file.write_text(yaml_content)
    config = load_config(cfg_file)
    assert config.broker.host == "localhost"
    assert config.refresh_rate == 2.0
    assert config.sensors[0].thresholds is None


def test_sensor_config_missing_required_fields():
    with pytest.raises(ValidationError):
        SensorConfig(name="x", sensor_type="temperature")  # missing mqtt_topic, unit


def test_framework_config_missing_sensors():
    with pytest.raises(ValidationError):
        FrameworkConfig()  # sensors is required


def test_sensor_config_invalid_type():
    with pytest.raises(ValidationError):
        SensorConfig(
            name="x",
            sensor_type="wind_speed",  # not in Literal
            mqtt_topic="t/x",
            unit="ms",
        )
