from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text

from bloom_iot.emitter.base import AbstractEmitter

if TYPE_CHECKING:
    from bloom_iot.adapter.models import SensorReading

_ALERT_COLORS = {
    "ok": "green",
    "warn": "yellow",
    "critical": "bold red",
}


class CliDashboard(AbstractEmitter):
    """Live Rich terminal dashboard, refreshed on every new reading."""

    def __init__(self, refresh_rate: float = 2.0) -> None:
        self._console = Console()
        self._readings: dict[str, SensorReading] = {}
        self._live = Live(
            self._build_table(),
            console=self._console,
            refresh_per_second=max(1, int(1 / refresh_rate)),
        )

    def __enter__(self) -> CliDashboard:
        self._live.start()
        return self

    def __exit__(self, *_) -> None:
        self._live.stop()

    def emit(self, reading: SensorReading) -> None:
        self._readings[reading.sensor_name] = reading
        self._live.update(self._build_table())

    def _build_table(self) -> Table:
        table = Table(
            title="[bold cyan]bloom-iot[/bold cyan] — Microgreen Monitor",
            show_header=True,
            header_style="bold magenta",
            expand=True,
        )
        table.add_column("Sensor", style="cyan", no_wrap=True)
        table.add_column("Type", style="dim")
        table.add_column("Value", justify="right")
        table.add_column("Unit", justify="left")
        table.add_column("Alert", justify="center")
        table.add_column("Last Seen", justify="right", style="dim")

        now = datetime.now(timezone.utc)
        for reading in sorted(self._readings.values(), key=lambda r: r.sensor_name):
            age_s = int((now - reading.timestamp).total_seconds())
            age_str = f"{age_s}s ago" if age_s < 60 else f"{age_s // 60}m ago"
            color = _ALERT_COLORS[reading.alert_level]
            alert_text = Text(reading.alert_level.upper(), style=color)
            table.add_row(
                reading.sensor_name,
                reading.sensor_type,
                f"{reading.normalized_value:.2f}",
                reading.unit,
                alert_text,
                age_str,
            )

        if not self._readings:
            table.add_row("[dim]Waiting for sensor data…[/dim]", "", "", "", "", "")

        return table
