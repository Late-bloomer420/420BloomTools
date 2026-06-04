from unittest.mock import MagicMock, call, patch


def test_mqtt_listener_subscribes_all_topics(broker_config, temp_sensor_config, humidity_sensor_config):
    with patch("bloom_iot.listener.mqtt_listener.mqtt.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        from bloom_iot.listener.mqtt_listener import MQTTListener
        listener = MQTTListener(broker_config, [temp_sensor_config, humidity_sensor_config])
        listener.start()

        mock_client.connect.assert_called_once_with("localhost", 1883, 60)
        mock_client.loop_start.assert_called_once()
        # on_connect triggers subscriptions; simulate it
        listener._on_connect(mock_client, None, None, 0)
        subscribe_calls = mock_client.subscribe.call_args_list
        subscribed_topics = [c[0][0] for c in subscribe_calls]
        assert "test/temp" in subscribed_topics
        assert "test/humidity" in subscribed_topics


def test_mqtt_listener_stop(broker_config, temp_sensor_config):
    with patch("bloom_iot.listener.mqtt_listener.mqtt.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        from bloom_iot.listener.mqtt_listener import MQTTListener
        listener = MQTTListener(broker_config, [temp_sensor_config])
        listener.start()
        listener.stop()

        mock_client.loop_stop.assert_called_once()
        mock_client.disconnect.assert_called_once()


def test_mqtt_listener_on_message_callback(broker_config, temp_sensor_config):
    with patch("bloom_iot.listener.mqtt_listener.mqtt.Client"):
        from bloom_iot.listener.mqtt_listener import MQTTListener
        listener = MQTTListener(broker_config, [temp_sensor_config])

        received = []
        listener.on_message(lambda topic, payload: received.append((topic, payload)))

        fake_msg = MagicMock()
        fake_msg.topic = "test/temp"
        fake_msg.payload = b"22.5"
        listener._on_message(None, None, fake_msg)

        assert len(received) == 1
        assert received[0] == ("test/temp", b"22.5")
