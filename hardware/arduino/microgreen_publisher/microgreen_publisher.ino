/*
 * bloom-iot Arduino Publisher
 * Hardware: ESP32 + DHT22 (temp/humidity) + capacitive soil moisture sensor
 * Libraries required (install via Arduino Library Manager):
 *   - PubSubClient by Nick O'Leary
 *   - DHT sensor library by Adafruit
 *   - Adafruit Unified Sensor
 *
 * Publishes plain float payloads every 5 seconds.
 * Topics must match your config/sensors.yaml.
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHT_PIN     4
#define SOIL_PIN    34          // analog ADC pin
#define DHT_TYPE    DHT22

const char* WIFI_SSID     = "YOUR_SSID";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* MQTT_BROKER   = "192.168.1.100";  // IP of machine running bloom-iot
const int   MQTT_PORT     = 1883;
const char* CLIENT_ID     = "esp32_grow_tent1";

// Topics — must match sensors.yaml
const char* TOPIC_TEMP     = "garden/tent1/temperature";
const char* TOPIC_HUMIDITY = "garden/tent1/humidity";
const char* TOPIC_SOIL     = "garden/tray1/soil_moisture";

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

void setup() {
    Serial.begin(115200);
    dht.begin();

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println(" connected");

    mqtt.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
    if (!mqtt.connected()) {
        reconnect();
    }
    mqtt.loop();

    float temp     = dht.readTemperature();       // degrees Celsius
    float humidity = dht.readHumidity();          // percent
    int   soilRaw  = analogRead(SOIL_PIN);
    // Map raw ADC (0–4095) to percent; capacitive sensors read HIGH when dry
    float soilPct  = 100.0f - (soilRaw / 4095.0f * 100.0f);

    if (!isnan(temp)) {
        mqtt.publish(TOPIC_TEMP, String(temp, 1).c_str());
        Serial.printf("temp: %.1f°C\n", temp);
    }
    if (!isnan(humidity)) {
        mqtt.publish(TOPIC_HUMIDITY, String(humidity, 1).c_str());
        Serial.printf("humidity: %.1f%%\n", humidity);
    }
    mqtt.publish(TOPIC_SOIL, String(soilPct, 1).c_str());
    Serial.printf("soil: %.1f%%\n", soilPct);

    delay(5000);
}

void reconnect() {
    while (!mqtt.connect(CLIENT_ID)) {
        Serial.println("MQTT connect failed, retrying in 2s...");
        delay(2000);
    }
    Serial.println("MQTT connected");
}
