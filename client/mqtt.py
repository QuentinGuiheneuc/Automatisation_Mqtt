#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import json
# import wiringpi
from threading import Thread
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

class Thread_custom(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,**self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    def terminate(self):
        self._running = False 


GPIO.setmode(GPIO.BCM)

def lire_fichier_Json(fichier):
    with open(fichier) as fichiers:
        return json.load(fichiers)

config = lire_fichier_Json("config.json")
for key in config["action"]:
    Button = config["action"][key]
    if Button["mode"] == "in":
        GPIO.setup(int(Button["pin"]), GPIO.IN)
    if Button["mode"] == "out":
        GPIO.setup(int(Button["pin"]), GPIO.OUT)
    if Button["mode"] == "pwm":
        GPIO.setup(int(Button["pin"]), 2)
    if Button["pullUpDnControl"] != "":
        if Button["pullUpDnControl"] == "up":
            pull = GPIO.PUD_UP
        if Button["pullUpDnControl"] == "down":
            pull = GPIO.PUD_DOWN
        GPIO.setup(int(Button["pin"]), GPIO.IN ,pull_up_down= pull)


statusBtn_1 = False
topic = config["mqtt"]["topic"]
uid = config["mqtt"]["uid"]
FichierClient = config["mqtt"]["name_client_flie"]
separation = config["mqtt"]["separation"]

def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc)+ " " +str(flags))

def on_message(client, obj, msg):
    payload = msg.payload.decode("utf-8")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    pay = payload.split(separation)
    if payload.startswith("401"): # demanded on client
        print(ecrire_fichier(FichierClient,pay[1]))
    if payload.startswith("402"):
        mqttc.publish("prise", "400{separation}{0}{separation}{1}".format(uid,returnTopic)) 
    if payload.startswith("403"):
        mqttc.publish("prise" , "404{separation}{0}".format(uid))
    
def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def ecrire_fichier(fichier,data):
    if is_fichier(fichier):        
        fichiers = open(fichier, "w")
        fichiers.write(data)
        fichiers.close()
        time.sleep(1)
        return lire_fichier(fichier)

def lire_fichier(fichier):
    if is_fichier(fichier):
        with open(fichier, "r") as fichiers:
            return fichiers.read()
    else:
        return ""

def is_fichier(Path):
    try:
        with open(Path, 'r') as f:
            return True
    except FileNotFoundError as e:
        return False
    except IOError as e:
        return False

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.username_pw_set(config["mqtt"]["username"], config["mqtt"]["password"])
mqttc.connect(config["mqtt"]["host"],config["mqtt"]["port"])


if lire_fichier(FichierClient) != "":
    returnTopic = lire_fichier(FichierClient)
else:
    returnTopic = uid

if is_fichier(FichierClient):
    if lire_fichier(FichierClient) == "":
        print("le fichier est vide")
        returnTopic = uid
        mqttc.subscribe(str(returnTopic), 0)
        mqttc.publish(topic, f"400{separation}{uid}{separation}{returnTopic}")
    else:
        returnTopic = lire_fichier(FichierClient)
        mqttc.subscribe(str(lire_fichier(FichierClient)), 0)
        print(lire_fichier(FichierClient))
else:
    print("le fichier est pas presant")
    mqttc.subscribe(str(returnTopic), 0)
    mqttc.publish(topic, f"400{separation}{uid}{separation}{returnTopic}")

mqttc.subscribe("listeObjet", 0)

def callback():
    rc = 0
    while rc == 0:
        rc = mqttc.loop()
    print("rc:", str(rc))


def envoie_mqtt(code,dis):
    mqttc.publish(topic,f"{code}{separation}{returnTopic}{separation}{json.dumps(dis)}")

def execute_pin(pin):
    for key in config["action"]:
        Button = config["action"][key]
        if Button["pin"] == pin:
            btnRead = GPIO.input(int(Button["pin"]))
            dis = {key: btnRead}
            if Button["type"] == "swich":
                if btnRead == 1:
                    envoie_mqtt(Button['mqtt']['code_ex'],dis)
                    if btnRead == 0:
                        envoie_mqtt(Button['mqtt']['code_ex'],dis)
            if Button["type"] == "button":
                if btnRead == 1:
                    envoie_mqtt(Button['mqtt']['code_ex'],dis)
        # message=""
        # if message != "":
        #     pay = message.split(separation)
        #     if pay[0] == Button["mqtt"]["code_in"]:
        #         if Button["type"] == "led":
                    
        #             if btnRead == 1:
        #                 GPIO.output(int(Button["pin"]), 0)
        #             else:
        #                 GPIO.output(int())


def while_wiringpi():
    for key in config["action"]:
        try:
            Buttons = config["action"][key]
            # if Buttons["type"] == "swich" and Buttons["type"] == "button":
            GPIO.add_event_detect(int(Buttons["pin"]), GPIO.RISING, callback=globals()["execute_pin"],bouncetime=300)
        except RuntimeError as erreur:
            print("Pin Double event ou pin non exsitence",erreur)

Thread_callback = Thread_custom(target=callback, name="callback")
Thread_callback.Daemon = True
Thread_callback.start()
while_wiringpi()
print(Thread_callback.is_alive())
