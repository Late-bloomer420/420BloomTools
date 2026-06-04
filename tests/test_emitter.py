import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from bloom_iot.adapter.models import SensorReading
from bloom_iot.emitter.json_emitter import JsonEmitter


@pytest.fixture
def sample_reading():
    return SensorReading(
        sensor_name="test_temp",
        sensor_type="temperature",
        raw_value=22.5,
        normalized_value=22.5,
        unit="°C",
        timestamp=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        alert_level="ok",
    )


def test_json_emitter_writes_to_file(tmp_path, sample_reading):
    out_file = tmp_path / "readings.json"
    with JsonEmitter(path=out_file) as emitter:
        emitter.emit(sample_reading)

    lines = out_file.read_text().strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["sensor_name"] == "test_temp"
    assert data["normalized_value"] == 22.5
    assert data["alert_level"] == "ok"


def test_json_emitter_appends_multiple(tmp_path, sample_reading):
    out_file = tmp_path / "readings.json"
    with JsonEmitter(path=out_file) as emitter:
        emitter.emit(sample_reading)
        emitter.emit(sample_reading)

    lines = out_file.read_text().strip().splitlines()
    assert len(lines) == 2


def test_json_emitter_datetime_is_iso8601(tmp_path, sample_reading):
    out_file = tmp_path / "readings.json"
    with JsonEmitter(path=out_file) as emitter:
        emitter.emit(sample_reading)

    data = json.loads(out_file.read_text().strip())
    assert data["timestamp"] == "2024-01-15T10:30:00Z"


def test_json_emitter_stdout(capsys, sample_reading):
    with JsonEmitter(path=None) as emitter:
        emitter.emit(sample_reading)

    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["sensor_name"] == "test_temp"


def test_cli_dashboard_can_be_constructed():
    from bloom_iot.emitter.cli_dashboard import CliDashboard
    dashboard = CliDashboard(refresh_rate=2.0)
    assert dashboard is not None
