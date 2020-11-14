# Telemetry Basestation

Base station consist on an MQTT broker and and MQTT Subscriber that forwards the events to Firebase.

# Node message format requirement
Nodes (MQTT Publishers) MUST follow this structure as the message being sent:

```
{
   "location":<location string>,
   "node_id":<unique UUID>,
   "data_type":<data type string>,
   "measurement_unit":<unit in string>,
   "timestamp":<epoch>,
   "value":<float>
}
```

Example:
```
{
   "location":"Laboratory",
   "node_id":"9ab93a61-bfad-442a-b551-5a155545bb60",
   "data_type":"Temperature",
   "measurement_unit":"Celsius",
   "timestamp":1604156438.187722,
   "value":25.33
}
```

# Usage

1. Set MQTT configuration at `mqtt_config.yml`
2. Place Firebase serviceAccount JSON file in a known location.
3. Set Firebase configuration at `firebase_config.yml`
4. Set Basestation configuration at `basestation_config.yml`
5. Run the MQTT broker:
```
cd src
py mqtt_broker.py
```
6. Run the MQTT Subscriber
```
cd src
py mqtt_subscriber_to_firebase.py
```

# Testing
Under `test_tools` there is an MQTT publisher sending temperature every minute based on openweather API.
1. Set openweather configuration at `openweather_config.yml`
2. Run the MQTT Publisher:
```
cd test_tools
py mqtt_publisher.py
```

