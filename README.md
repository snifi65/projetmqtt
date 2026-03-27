équipe vincent côté

lien github: https://github.com/snifi65/projetmqtt

Convention topic:

topic sensor: ahuntsic/aec-iot/b3/Vincent/pi01/sensors/temperature/value

topic subscriber: ahuntsic/aec-iot/b3/Vincent/pi01/actuators/led/cmd

topic mariadb: ahuntsic/aec-iot/b3/Vincent/pi01

tester mosquitto:

abonnement: mosquitto_sub -h localhost -t "v1/sensor/+" -v

publier: mosquitto_pub -h localhost -t "v1/sensor/temperature" -m '{"device_id": "test_01", "value": 25}'

vérifier mariadb:

mariadb -u user -p iot_db

Preuve avec photo:

![preuve1](C:\Users\vinc7\Downloads\images\preuve1.png)

![preuve2](C:\Users\vinc7\Downloads\images\preuve2.png)
