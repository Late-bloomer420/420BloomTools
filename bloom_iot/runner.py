from __future__ import annotations

import argparse
import contextlib
import platform
import signal
import time

from bloom_iot.adapter.normalizer import DataAdapter
from bloom_iot.config import load_config
from bloom_iot.emitter.base import AbstractEmitter
from bloom_iot.emitter.cli_dashboard import CliDashboard
from bloom_iot.emitter.json_emitter import JsonEmitter
from bloom_iot.listener.mqtt_listener import MQTTListener


def _build_emitters(args: argparse.Namespace, refresh_rate: float) -> list[AbstractEmitter]:
    emitters: list[AbstractEmitter] = []
    mode = args.output
    if mode in ("dashboard", "both"):
        emitters.append(CliDashboard(refresh_rate=refresh_rate))
    if mode in ("json", "both"):
        emitters.append(JsonEmitter(path=args.json_out))
    return emitters


def main() -> None:
    parser = argparse.ArgumentParser(
        description="bloom-iot: Listen & Adapt IoT Framework for plant monitoring"
    )
    parser.add_argument("--config", default="config/sensors.yaml",
                        help="Path to sensors YAML config (default: config/sensors.yaml)")
    parser.add_argument("--output", choices=["dashboard", "json", "both"], default="dashboard",
                        help="Output mode (default: dashboard)")
    parser.add_argument("--json-out", default=None,
                        help="File path for JSON output (required when --output=json or both)")
    args = parser.parse_args()

    if args.output in ("json", "both") and args.json_out is None:
        parser.error("--json-out is required when --output is 'json' or 'both'")

    config = load_config(args.config)
    adapter = DataAdapter(config.sensors)
    emitters = _build_emitters(args, config.refresh_rate)
    listener = MQTTListener(config.broker, config.sensors)

    def on_message(topic: str, payload: str | bytes) -> None:
        reading = adapter.adapt(topic, payload)
        if reading:
            for emitter in emitters:
                emitter.emit(reading)

    listener.on_message(on_message)

    with contextlib.ExitStack() as stack:
        for emitter in emitters:
            stack.enter_context(emitter)
        listener.start()
        print(f"bloom-iot listening on {config.broker.host}:{config.broker.port} "
              f"— {len(config.sensors)} sensor(s) configured. Press Ctrl+C to stop.")
        try:
            if platform.system() != "Windows":
                signal.pause()
            else:
                while True:
                    time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            listener.stop()


if __name__ == "__main__":
    main()
