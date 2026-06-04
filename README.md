# 420BloomTools

**"The Automagic Gardener"** — a toolkit for hobbyists and DIY enthusiasts that bridges hardware (Arduino, Raspberry Pi) with code for real-world plant monitoring and home automation.

## Focus Areas

1. **Microgreen Monitor** — monitor and automate care for indoor plants using low-cost sensors via the `bloom-iot` framework (see below).
2. **Wax-on, Wax-Off Automations** — gamify daily chores: automate watering reminders, calendar-based tasks, and custom timers.

---

## bloom-iot: Listen & Adapt IoT Framework

A lightweight Python framework that **listens** to sensor data from Arduino/Raspberry Pi hardware via MQTT and **adapts** raw readings into normalized, threshold-aware data ready for a live dashboard or downstream pipelines.

### Architecture

```
MQTT Broker ──► SensorListener ──► DataAdapter ──► Emitter
                 (paho-mqtt)        (normalize,      (Rich CLI
                                     threshold)       or JSON)
```

### Quick Start

```bash
# 1. Install
pip install -e ".[dev]"

# 2. Configure your sensors
cp config/sensors.example.yaml config/sensors.yaml
# edit config/sensors.yaml for your broker IP and sensor topics

# 3. Run
bloom-iot --config config/sensors.yaml --output dashboard
```

### Supported Sensors

| Type | Units | Example Hardware |
|---|---|---|
| Temperature | Celsius (Fahrenheit auto-converted) | DHT22, DS18B20 |
| Humidity | % | DHT22, SHT31 |
| Soil Moisture | % | Capacitive analog sensor |
| Light Intensity | lux | BH1750, TSL2561 |

### MQTT Payload Format

Publish a plain float or a JSON object — both are accepted:

```
22.5                          # plain float (Arduino default)
{"value": 22.5}               # JSON with "value" key
{"temperature": 22.5}         # JSON with sensor-type key
```

### Output Modes

```bash
# Live terminal dashboard (default)
bloom-iot --output dashboard

# Newline-delimited JSON file
bloom-iot --output json --json-out data/readings.json

# Both simultaneously
bloom-iot --output both --json-out data/readings.json
```

### Hardware Setup

- `hardware/arduino/microgreen_publisher/` — ESP32 + DHT22 + soil sensor sketch (PubSubClient)
- `hardware/raspberry_pi/dht22_mqtt_publisher.py` — RPi + DHT22 + BH1750 publisher

### Running Tests

```bash
pytest --cov=bloom_iot tests/
```

Tests require no running broker — paho is fully mocked.

### Threshold Alerting

Configure `warn` and `critical` bands per sensor in `sensors.yaml`. The dashboard color-codes rows automatically:

- **Green** — ok
- **Yellow** — warn
- **Red/Bold** — critical

### Project Structure

```
bloom_iot/          Python package (listener, adapter, emitter)
config/             Sensor YAML configs (example provided)
hardware/           Arduino sketches and Raspberry Pi publishers
tests/              pytest test suite
```
