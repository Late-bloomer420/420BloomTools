#!/usr/bin/env python3
"""
bloom-iot Raspberry Pi Publisher
Hardware: Raspberry Pi + DHT22 on GPIO 4 + optional BH1750 light sensor (I2C)

Install dependencies:
    pip install paho-mqtt Adafruit-DHT smbus2

Usage:
    python3 dht22_mqtt_publisher.py

Topics published must match your config/sensors.yaml.
"""

import time

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

BROKER_HOST = "localhost"   # change if broker runs on another machine
BROKER_PORT = 1883
CLIENT_ID = "rpi_grow_tent1"

TOPIC_TEMP     = "garden/tent1/temperature"
TOPIC_HUMIDITY = "garden/tent1/humidity"
TOPIC_LIGHT    = "garden/tent1/light"

PUBLISH_INTERVAL = 5  # seconds

client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
client.connect(BROKER_HOST, BROKER_PORT)
client.loop_start()


def read_bh1750_lux() -> float | None:
    """Read lux from BH1750 via I2C (address 0x23). Returns None if unavailable."""
    try:
        import smbus2
        bus = smbus2.SMBus(1)
        data = bus.read_i2c_block_data(0x23, 0x20, 2)
        lux = (data[1] + (256 * data[0])) / 1.2
        return round(lux, 1)
    except Exception:
        return None


try:
    import Adafruit_DHT

    DHT_SENSOR = Adafruit_DHT.DHT22
    DHT_PIN = 4

    print(f"bloom-iot publisher running — sending to {BROKER_HOST}:{BROKER_PORT}")
    print("Press Ctrl+C to stop.")

    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if temperature is not None:
            client.publish(TOPIC_TEMP, f"{temperature:.1f}")
            print(f"temp: {temperature:.1f}°C")

        if humidity is not None:
            client.publish(TOPIC_HUMIDITY, f"{humidity:.1f}")
            print(f"humidity: {humidity:.1f}%")

        lux = read_bh1750_lux()
        if lux is not None:
            client.publish(TOPIC_LIGHT, f"{lux:.1f}")
            print(f"light: {lux:.1f} lux")

        time.sleep(PUBLISH_INTERVAL)

except ImportError:
    print("Adafruit_DHT not installed. Run: pip install Adafruit-DHT")
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
