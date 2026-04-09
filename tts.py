import subprocess
import json
import time
import paho.mqtt.client as mqtt
from gpiozero import LED

BROKER = "10.0.0.79"
PORT = 1883
CLIENT_ID = "pi01_master_controller"
TOPIC_TTS = f"ahuntsic/aec-iot/b3/Vincent/pi01/tts"
TOPIC_CMD = f"ahuntsic/aec-iot/b3/Vincent/pi01/actuators/led/cmd"
TOPIC_STATE = f"ahuntsic/aec-iot/b3/Vincent/pi01/actuators/led/state"

HOTWORD = "assistant"
led = LED(17)

def speak(text, langue="fr", debit=150):
    print(f"[VOIX]: {text}")
    subprocess.run(["espeak-ng", "-v", langue, "-s", str(debit), text])

def publish_action(client, action_val):
    payload = json.dumps({"state": action_val, "ts": time.time()})
    client.publish(TOPIC_CMD, payload, qos=1)

def check_status():
    return "allumée" if led.is_lit else "éteinte"

def process_intent(client, text):
    text = text.lower().strip()
    
    if "allume" in text:
        publish_action(client, "on")
        led.on() 
        speak("J'ai allumé la lampe")
        
    elif "eteins" in text:
        publish_action(client, "off")
        led.off()
        speak("La lampe est maintenant éteinte")
        
    elif "clignote" in text:
        speak("Je fais clignoter la lampe")
        for i in range(15):
            led.on()
            time.sleep(0.3)
            led.off()
            time.sleep(0.3)
        publish_action(client, "off")
        
    elif "etat" in text:
        etat = check_status()
        speak(f"La lampe est actuellement {etat}")
        
    elif "nuit" in text:
        speak("Mode nuit activé.")
        for i in range(15):
            led.on()
            time.sleep(0.8)
            led.off()
            time.sleep(0.8)
        publish_action(client, "off")
        
    else:
        speak("Commande non reconnue, veuillez répéter.")

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"En attente du mot: {HOTWORD}")
    client.subscribe(TOPIC_TTS)

def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip()
    
    if payload.lower().startswith(HOTWORD.lower()):
        commande = payload[len(HOTWORD):].strip()
        
        if not commande:
            speak("Je vous écoute")
        else:
            print(f"Intention détectée pour : {commande}")
            process_intent(client, commande)
    else:
        print(f"Message sans mot-clé : {payload}")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()