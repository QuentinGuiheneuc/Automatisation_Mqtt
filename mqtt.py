#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import json

username = "serv"
password = "quentin"
hostname = "192.168.1.39"
port = 1883
is_client = False

topic = "prise"
uid = 1523698745
FichierClient = "client.txt"

def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc)+ " " +str(flags))

def on_message(client, obj, msg):
    payload = msg.payload.decode("utf-8")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload) )
    if payload.startswith("401"): # demanded on client
        pay = payload.split(";")
        print(pay[1])
        print(ecrire_fichier(FichierClient,pay[1]))
    if payload.startswith("402"):
        print("402")
        mqttc.publish("prise", "400;{0};{1}".format(uid,returnTopic)) 
    if payload.startswith("403"):
        mqttc.publish("prise" , "404;{0}".format(uid))
    if payload.startswith("200"):
        pay = payload.split(";")
        print(pay[2])
        json_convert = json.loads(pay[2])
        #json_e = json.loads('{}'.format(json_convert))
        print(json_convert["Temps"])
       # print(json.loads(json_convert))
def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)

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

mqttc.username_pw_set(username, password)
mqttc.connect(hostname,port)

if lire_fichier(FichierClient) != "":
    returnTopic = lire_fichier(FichierClient)
else:
    returnTopic = uid

if is_fichier(FichierClient):
    print(lire_fichier(FichierClient))
    mqttc.subscribe(str(lire_fichier(FichierClient)), 0)
else:
    print("le fichier est pas presant")
    mqttc.subscribe(str(returnTopic), 0)
    mqttc.publish(topic, "400;{0};{1}".format(uid,returnTopic))
  
mqttc.subscribe("listeObjet", 0)

rc = 0
while rc == 0:
    rc = mqttc.loop()

print("rc: " + str(rc))