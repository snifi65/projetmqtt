import paho.mqtt.client as mqtt
import os

BROKER = "10.130.128.49"
TOPIC_TTS = "ahuntsic/aec-iot/b3/Vincent/pi01/tts"

def on_message(client, userdata, msg):
    texte = msg.payload.decode()
    print(f"En train de dire : {texte}")
    os.system(f"espeak -v fr+f3 '{texte}'")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883)
client.subscribe(TOPIC_TTS)

print("Attente de messages à vocaliser...")
client.loop_forever()