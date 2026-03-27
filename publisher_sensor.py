from __future__ import annotations
import json
import random
import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

BROKER_HOST = "172.20.10.2"
BROKER_PORT = 1883
KEEPALIVE_S = 60
CLIENT_ID = "oXCVQwqXdf_publisher"
TEAM = "Vincent"
DEVICE = "pi01"
TOPIC_JSON = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/sensors/temperature"
TOPIC_VALUE = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/sensors/temperature/value"
TOPIC_ONLINE = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/status/online"
QOS_SENSOR = 0
QOS_STATUS = 1
PUBLISH_PERIOD_S = 2.0
def read_temperature_c() -> float:

 return round(20.0 + random.random() * 5.0, 2)
connected = False
def on_connect(client, userdata, flags, reason_code, properties=None):
 global connected
 print(f"[CONNECT] reason_code={reason_code}")
 connected = (reason_code == 0)
def on_disconnect(client, userdata, reason_code, properties=None):
 global connected
 print(f"[DISCONNECT] reason_code={reason_code}")
 connected = False
client = mqtt.Client(
 client_id=CLIENT_ID,
 protocol=mqtt.MQTTv311 
)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.will_set(
 topic=TOPIC_ONLINE,
 payload="offline",
 qos=QOS_STATUS,
 retain=True
)
client.reconnect_delay_set(min_delay=1, max_delay=30)
client.connect_async(BROKER_HOST, BROKER_PORT, keepalive=KEEPALIVE_S)
client.loop_start()

try:
    client.publish(TOPIC_ONLINE, "online", qos=QOS_STATUS, retain=True)
    while True:
         if not connected:
            print("[WAIT] en attente de connexion MQTT...")
            time.sleep(1.0)
            continue
         temperature_c = read_temperature_c()
         payload = {
            "device_id": DEVICE,
            "sensor": "temperature",
            "value": temperature_c,
            "unit": "C",
            "ts": datetime.now(timezone.utc).isoformat()
        }
         client.publish(TOPIC_JSON, json.dumps(payload), qos=QOS_SENSOR, retain=False)
         client.publish(TOPIC_VALUE, str(temperature_c), qos=QOS_SENSOR, retain=False)
         print(f"[PUB] {TOPIC_JSON} -> {payload}")
         time.sleep(PUBLISH_PERIOD_S)
except KeyboardInterrupt:
 print("\n[STOP] arrêt demandé (Ctrl+C)")
finally:
 client.publish(TOPIC_ONLINE, "offline", qos=QOS_STATUS, retain=True)
 client.loop_stop()
 client.disconnect() 
