import speech_recognition as sr
import paho.mqtt.client as mqtt
import re
import RPi.GPIO as GPIO
import time
from datetime import datetime

LED_PIN = 17  
BROKER = "10.130.128.49"
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
try:
    client.connect(BROKER, 1883, 60)
    client.loop_start()
except Exception as e:
    print(f"Erreur de connexion au broker : {e}")

def speak(message):
    """Envoie le texte au système TTS pour confirmation vocale."""
    print(f"Système : {message}")
    client.publish(TOPIC_TTS, message)

def interpreter_commande(texte):
    global etat_actuel
    t = texte.lower().strip()
    
    if re.search(r"allume|active|ouvre", t) and re.search(r"lampe|lumière", t):
        etat_actuel = "allumée"
        return "on", "j'allume la lumière."
    
    elif re.search(r"éteins|ferme|coupe", t) and re.search(r"lampe|lumière", t):
        etat_actuel = "éteinte"
        return "off", "j'ai éteint la lampe."
    
    elif re.search(r"clignote|clignoter|flash", t):
        return "clignote", "Je fais clignoter la lampe immédiatement."
    
    elif re.search(r"nuit|sommeil|réduit", t):
        etat_actuel = "en mode nuit"
        return "nuit", "Le mode nuit est activé."
    
    elif re.search(r"état|statut|comment va", t):
        return "get_status", f"La lampe est actuellement {etat_actuel}."
    
    return None, "Désolé, je n'ai pas compris cette commande."

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
        pwm.ChangeDutyCycle(100 if "allumée" in etat_actuel else 0)

def demarrer():
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    
    with sr.Microphone(device_index=MICRO_INDEX) as source:
        print("Calibrage du bruit ambiant...")
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"Prêt ! Dites '{HOT_WORD}' pour commencer.")

        while True:
            try:
                audio = r.listen(source, timeout=None)
                recon_text = r.recognize_google(audio, language="fr-FR").lower()
                
                if HOT_WORD in recon_text:
                    speak("Oui ? Je vous écoute.") 
                    
                    audio_cmd = r.listen(source, timeout=5)
                    raw_text = r.recognize_google(audio_cmd, language="fr-FR")
                    print(f"Entendu : {raw_text}")

                    intention, feedback = interpreter_commande(raw_text)
                    
                    if intention:
                        executer_physique(intention)
                    
                    speak(feedback)

            except sr.UnknownValueError:
                pass
            except sr.WaitTimeoutError:
                speak("Je n'ai rien entendu.")
            except Exception as e:
                print(f"Erreur : {e}")

if __name__ == "__main__":
    try:
        demarrer()
    except KeyboardInterrupt:
        print("\nArrêt du système...")
        pwm.stop()
        GPIO.cleanup()
        client.loop_stop()
        client.disconnect()