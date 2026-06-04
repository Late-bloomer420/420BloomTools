from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from bloom_iot.listener.base import AbstractSensorListener

if TYPE_CHECKING:
    from bloom_iot.config import BrokerConfig, SensorConfig


class MQTTListener(AbstractSensorListener):
    def __init__(self, broker: BrokerConfig, sensors: list[SensorConfig]) -> None:
        self._broker = broker
        self._topics = [s.mqtt_topic for s in sensors]
        self._callback: Callable[[str, str | bytes], None] | None = None

        protocol = mqtt.MQTTv5 if broker.mqtt_version == "5.0" else mqtt.MQTTv311
        self._client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            protocol=protocol,
        )

        if broker.username:
            self._client.username_pw_set(broker.username, broker.password)

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def on_message(self, callback: Callable[[str, str | bytes], None]) -> None:
        self._callback = callback

    def start(self) -> None:
        self._client.connect(self._broker.host, self._broker.port, self._broker.keepalive)
        self._client.loop_start()

    def stop(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None) -> None:
        for topic in self._topics:
            client.subscribe(topic, qos=1)

    def _on_message(self, client, userdata, message) -> None:
        if self._callback is not None:
            self._callback(message.topic, message.payload)
