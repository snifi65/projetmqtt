import speech_recognition as sr
import paho.mqtt.client as mqtt
import re
import RPi.GPIO as GPIO
import time
from datetime import datetime

LED_PIN = 17  
BROKER = "192.168.5.17"
TOPIC_TTS = "ahuntsic/aec-iot/b3/Vincent/pi01/tts"
HOT_WORD = "assistant"
MICRO_INDEX = 1 

etat_actuel = "éteinte"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
pwm = GPIO.PWM(LED_PIN, 100)
pwm.start(0)

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

def speak(message):
    print(f"Système : {message}")
    client.publish(TOPIC_TTS, message)

def interpreter_commande(texte):
    global etat_actuel
    t = texte.lower().strip()
    
    if re.search(r"allume|active|ouvre", t) and re.search(r"lampe|lumière", t):
        etat_actuel = "allumée"
        return "on", "La lampe est maintenant allumée."
    
    elif re.search(r"éteins|ferme|coupe", t) and re.search(r"lampe|lumière", t):
        etat_actuel = "éteinte"
        return "off", "J'ai éteint la lampe."
    
    elif re.search(r"clignote|clignoter|flash", t):
        return "clignote", "D'accord, je fais clignoter la lampe."
    
    elif re.search(r"nuit|sommeil|réduit", t):
        etat_actuel = "en mode nuit (faible intensité)"
        return "nuit", "Le mode nuit est activé."
    
    elif re.search(r"état|statut|comment va", t):
        return "get_status", f"La lampe est actuellement {etat_actuel}."
    
    return None, None

def executer_physique(intention):
    if intention == "on":
        pwm.ChangeDutyCycle(100)
    elif intention == "off":
        pwm.ChangeDutyCycle(0)
    elif intention == "nuit":
        pwm.ChangeDutyCycle(10)
    elif intention == "clignote":
        for _ in range(5):
            pwm.ChangeDutyCycle(100); time.sleep(0.3)
            pwm.ChangeDutyCycle(0); time.sleep(0.3)
        pwm.ChangeDutyCycle(100 if etat_actuel == "allumée" else 0)

def demarrer():
    r = sr.Recognizer()
    with sr.Microphone(device_index=MICRO_INDEX) as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Dites assistant pour commencer")

        while True:
            try:
                audio = r.listen(source, timeout=None)
                if HOT_WORD in r.recognize_google(audio, language="fr-FR").lower():
                    speak("Je vous écoute")
                    
                    audio_cmd = r.listen(source, timeout=5)
                    raw_text = r.recognize_google(audio_cmd, language="fr-FR")
                    print(f"Entendu : {raw_text}")

                    intention, feedback = interpreter_commande(raw_text)
                    
                    if intention:
                        executer_physique(intention)
                        if feedback: speak(feedback)
                    else:
                        speak("Commande non reconnue.")
            except:
                pass

if __name__ == "__main__":
    try:
        demarrer()
    except KeyboardInterrupt:
        pwm.stop(); GPIO.cleanup()

