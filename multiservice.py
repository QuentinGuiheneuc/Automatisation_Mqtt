#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Match
import paho.mqtt.client as mqtt
import time
import mysql.connector
import json
import socket, multiprocessing
import os
import random
import datetime
from threading import Thread

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
    def stop(self):
        self._running = False 


def lire_fichier_Json(fichier):
    with open(fichier) as fichiers:
        return json.load(fichiers)


config = lire_fichier_Json("config.json")
client = mqtt.Client(
    config["mqtt"]["clientId"], userdata=True
)
client.username_pw_set(
    config["mqtt"]["username"], config["mqtt"]["password"]
)
client.connect(
    config["mqtt"]["serverUrl"], config["mqtt"]["port"]
)
separation = config["mqtt"]["separation"]
host = config["socket"]["host"]
port = config["socket"]["port"]
nb_workers = config["socket"]["nb_workers"]
is_start = False
buff_socket = config["socket"]["buff"]
separation_socket = config["socket"]["separation"]
white_list_ip_socket = config["socket"]["white_list_ip"]
encode_socket = config["socket"]["encode"]
user_socket = ""
look = False
mydb = mysql.connector.connect(
    host=config["mysql"]["host"],
    port=config["mysql"]["port"],
    user=config["mysql"]["user"],
    password=config["mysql"]["password"],
    database=config["mysql"]["database"],
)


def error():
    return lire_fichier_Json("erreur.json")


def list_error(code_in):
    list = []
    for code in error():
        list.append(code)
    return not list.count(code_in)


def print_titreTopic():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT topic FROM `mqtttopic` WHERE active = 1")
    myresult = mycursor.fetchall()
    text = []
    for topic in myresult:
        for item in topic:
            text.append(item)
    return text


def ecrire_fichier(fichier, data):
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
        with open(Path, "r") as f:
            return True
    except FileNotFoundError as e:
        return False
    except IOError as e:
        return False


def cache_(bbd, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    pay = payload.split(";")
    if int(pay[0]) < 300:
        print("cache true")
        name_client = pay[1]
        mycursor = bbd.cursor()
        sql = "SELECT id_client FROM `mqttcache` WHERE `id_client` = (SELECT id_client FROM `mqttclient` WHERE client = '{0}')".format(name_client)
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        print(myresult)
        if myresult != []:
            sql = f"UPDATE `mqttcache` SET `ressult`='{payload}' WHERE `id_client` = (SELECT id_client FROM `mqttclient` WHERE client = '{name_client}')"
            mycursor.execute(sql)
            bbd.commit()
        else:
            sql = f"INSERT INTO `mqttcache`(`id_topic`, `id_client`, `ressult`) VALUES ((SELECT id_topic FROM `mqtttopic` WHERE topic = '{topic}'),(SELECT id_client FROM `mqttclient` WHERE client = '{name_client}'), '{payload}')"
            mycursor.execute(sql)
            bbd.commit()


def add_client(bbd, uid):
    mycursor = bbd.cursor()
    mycursor.execute(
        "SELECT client,uid FROM `mqttclient` WHERE `uid` = "
        + uid
    )
    myresult = mycursor.fetchall()
    print(myresult)
    if myresult == []:
        client = random.randrange(1000000000, 9999999999)
        sql = "INSERT INTO mqttclient (client, uid) VALUES (%s, %s)"
        val = (client, uid)
        mycursor.execute(sql, val)
        bbd.commit()
        print("Inserted")
        mycursor.execute(
            "SELECT client,uid FROM `mqttclient` WHERE `uid` = "
            + uid
        )
        myresult = mycursor.fetchall()
        for line in myresult:
            return line[0]
    elif myresult != []:
        for line in myresult:
            return line[0]


def notify_error(bbd, message):
    jjs = error()
    payload = message.payload.decode("utf-8")
    for line in jjs:
        if payload.startswith(line):
            pay = payload.split(";")
            code_error = pay[0]
            client = pay[1]
            dateNow = datetime.datetime.now()
            titre = "MQTT"
            sql = "INSERT INTO notification (titre, text, type,icon,date,color) VALUES (%s, %s,%s, %s,%s, %s)"
            for value in jjs:
                if value == code_error:
                    key = jjs[value]
                    text = key["text"].format(client)
                    val = (
                        titre,
                        text,
                        key["types"],
                        "icons/{0}".format(key["icon"]),
                        dateNow,
                        key["color"],
                    )
                    mycursor = bbd.cursor()
                    mycursor.execute(sql, val)
                    bbd.commit()


def initListeObjet(bbd):
    mycursor = bbd.cursor()
    sql = "UPDATE `mqttclient` SET is_alive = 0"
    mycursor.execute(sql)
    bbd.commit()
    print("all is_alive = 0")


def listeObjet(bbd, message):
    payload = message.payload.decode("utf-8")
    pay = payload.split(";")
    uid = pay[1]
    mycursor = bbd.cursor()
    mycursor.execute(
        "SELECT client,uid FROM `mqttclient` WHERE `uid` = "
        + uid
    )
    myresult = mycursor.fetchall()
    print(myresult)
    if myresult != []:
        sql = "UPDATE `mqttclient` SET is_alive = %s WHERE uid = %s"
        val = (1, uid)
        mycursor.execute(sql, val)
        bbd.commit()


def liste_code_in(bbd, code_in):
    rek = "SELECT code_in FROM `mqttexecut`"
    mycursor = bbd.cursor()
    mycursor.execute(rek)
    myresult = mycursor.fetchall()
    liste = []
    for result in myresult:
        for item in result:
            liste.append(item)
    return liste.count(code_in)

def function_Update(bdd,id, object):
    rek = """
       UPDATE `mqttexecut` SET `function`='{}' WHERE id = {}""".format(
            json.dumps(object), int(id)
        )
    print(rek)
    mycursor = bdd.cursor()
    mycursor.execute(rek)


def execute(bdd, message, mqtt,separation):

    topic = message.topic
    payload = message.payload.decode("utf-8")
    pay = payload.split(separation)
    codeIn = pay[0]
    print("execute", codeIn, list_error(pay[0]))

    if list_error(pay[0]) and liste_code_in(bdd, codeIn):
        clientIn = pay[1]
        rek = """
            SELECT id,mqc_e.client,mqc.client,mqe.code_ex,mqe.topic_ex,mqe.condition,mqe.function  FROM `mqttexecut` as mqe 
            INNER JOIN `mqttclient` as mqc ON mqe.client_id_in = mqc.id_client
            INNER JOIN `mqttclient` as mqc_e ON mqe.client_id_ex = mqc_e.id_client 
            WHERE mqe.code_in = '{0}' and mqe.topic_in = '{1}' and mqc.client = '{2}'""".format(
            codeIn, topic, clientIn
        )
        print(rek)
        mycursor = bdd.cursor()
        mycursor.execute(rek)
        myresult = mycursor.fetchall()
        print(myresult)
        if myresult != []:
            for result in myresult:
                id = result[0]
                client_ex = result[1]
                client_in = result[2]
                code_ex = result[3]
                topic_ex = result[4]
                if result[5] != "":
                    # print(result[4])
                    conditionJsonBdd = json.loads(result[5])
                    
                    if len(pay) > 2:
                        print(pay[2])
                        conditionJsonIn = json.loads(pay[2])
                    for (keyobj,valueobj,) in conditionJsonIn.items():
                        for (keybdd,valuebdd) in conditionJsonBdd.items():
                            if keyobj == keybdd:
                                exe = executeConsition(int(valueobj),valuebdd["condition"],int(valuebdd["value"]))
                                if result[6] != "":
                                    functionJsonBdd = json.loads(result[6])
                                    functionJsonBdd_ = json.loads(result[6])
                                    valueJsonBdd = functionJsonBdd["function"]
                                    for key,value in valueJsonBdd.items():
                                        print(key,value)
                                        if key == "swich":
                                            if value["value"] == True:
                                                functionJsonBdd_["function"][key]["value"] = False
                                                function_Update(bdd,id,functionJsonBdd_)
                                                dis = {valuebdd["objet"]: valueJsonBdd[key]["value"]}
                                            elif value["value"] == False:
                                                functionJsonBdd_["function"][key]["value"] = True
                                                function_Update(bdd,id,functionJsonBdd_)
                                                dis = {valuebdd["objet"]: valueJsonBdd[key]["value"]}
                                        if key == "button":
                                            dis = {valuebdd["objet"]: exe}
                                    message = f"{code_ex}{separation}{client_ex}{separation}{json.dumps(dis)}"
                                    print("message", message)
                                mqtt.publish(
                                    client_ex, message, 0
                                )
        else:
            print("not exe")


def executeConsition(value_1, condition, value_2):
    if condition == "==":
        return value_1 == value_2
    if condition == "!=":
        return value_1 != value_2
    if condition == "<":
        return value_1 < value_2
    if condition == ">":
        return value_1 > value_2
    if condition == "<=":
        return value_1 <= value_2
    if condition == ">=":
        return value_1 >= value_2

# MQTT
def on_execut(cliente, userdata, message):
    mydb1 = mysql.connector.connect(
        host=config["mysql"]["host"],
        user=config["mysql"]["user"],
        password=config["mysql"]["password"],
        database=config["mysql"]["database"],
    )

    payload = message.payload.decode("utf-8")
    print(
        " < received message "
        + payload
        + " "
        + message.topic
    )
    notify_error(mydb1, message)
    if payload.startswith("400"):  # demanded on client
        pay = payload.split(separation)
        CLient = add_client(mydb1, pay[1])
        client.publish(
            pay[2], f"401{separation}{CLient}", 1
        )
        CLient = ""
    if payload.startswith("404"):
        print(listeObjet(mydb1, message))
    if payload.startswith("405"):
        call_All_Objet()
    execute(mydb1, message, client, separation)
    cache_(mydb1, message)
    mydb1.close()


def on_publish(client, userdata, mid):
    print(" > published message: {}".format(mid))


def on_subscribe(client, obj, mid, granted_qos):
    print(
        "Subscribed: " + str(mid) + " " + str(granted_qos)
    )


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection.{str(userdata)}")

def callback():
    rc = 0
    while rc == 0:
        if is_start:
            rc = client.loop()

client.on_message = on_execut
client.on_subscribe = on_subscribe
client.on_publish = on_publish
client.on_disconnect = on_disconnect

def call_All_Objet():
    initListeObjet(mydb)
    client.publish("listeObjet", "403")


def liste_client():
    rek = "SELECT id_client,client,uid,is_alive FROM `mqttclient`"
    mycursor = mydb.cursor()
    mycursor.execute(rek)
    myresult = mycursor.fetchall()
    print(myresult)
    dis = {}
    i = 0
    for line in myresult:
        dis_1 = {"client": line[0],"client": line[1], "uid": line[2],"is_alive": bool(line[3])}
        dis[str(i)] = dis_1
        i = i+1
    return json.dumps(dis)


def liste_cache():
    rek = "SELECT `id_topic`, `id_client`, `ressult` FROM `mqttcache`"
    mycursor = mydb.cursor()
    mycursor.execute(rek)
    myresult = mycursor.fetchall()
    print(myresult)
    return myresult

def add_client(dbb, name, uid):
    try:
        sql = "INSERT INTO mqttclient (client, uid, is_alive) VALUES (%s,%s,%s)"
        val = (name, uid, 0)
        mycursor = dbb.cursor()
        mycursor.execute(sql, val)
        return "Client Mqtt Ajouter"
    except mysql.connector.errors.IntegrityError as e:
        print(f"erreur_{separation_socket}{e}".encode(encode_socket))
        conn.sendall(f"erreur_{separation_socket}{e}".encode(encode_socket))

def update_client(dbb, name, uid):
    try:
        sql = f"UPDATE `mqttclient` SET `client`='{name}' WHERE `uid` = {uid}"
        mycursor = dbb.cursor()
        mycursor.execute(sql)
    except mysql.connector.errors.IntegrityError as e:
        print(f"erreur_{separation_socket}{e}".encode("utf-8"))
        conn.sendall(f"erreur_{separation_socket}{e}".encode("utf-8"))

def cache_topic(topic):
    mydb = mysql.connector.connect(
        host=config["mysql"]["host"],
        port=config["mysql"]["port"],
        user=config["mysql"]["user"],
        password=config["mysql"]["password"],
        database=config["mysql"]["database"],
    )
    mycursor = mydb.cursor()
    mycursor.execute(
        f"SELECT (SELECT client FROM `mqttclient` WHERE id_client =  mqca.id_client ) ,  mqca.ressult FROM mqttcache as mqca WHERE mqca.id_topic = (SELECT `id_topic` FROM `mqtttopic` WHERE `topic` = '{topic}')"
    )
    myresult = mycursor.fetchall()
    dis = {}
    i = 0
    for topic in myresult:
        resulta_ = topic[1].split(separation)
        dis_1 = {
            "client": topic[0],
            "topic": resulta_[0],
            "value": json.loads(resulta_[2]),
        }
        dis[str(i)] = dis_1
        i += 1
    # print(json.dumps(dis))
    mydb.close()
    return json.dumps(dis)

def affiche_list_function(function):
    dis = {}
    dis_2 = {}
    disjson = config["function"][function]
    if function == "swich":
        dis[function] = disjson
    if function == "button":
        dis[function] = disjson
    if function == "va&vi":
        dis[function] = disjson
    dis_2["function"] = dis
    return json.dumps(dis_2)
    
print(affiche_list_function("swich"))
print(affiche_list_function("button"))
print(affiche_list_function("va&vi"))

def add_execut(dbb,code_in="",code_ex="",topic_in="",topic_ex="",id_client_in="",id_client_ex="",condition="",function_=""):
    try:
        sql = f"""INSERT INTO mqttexecut (code_in,code_ex,topic_in,topic_ex,id_client_in,id_client_ex,condition,function) 
        VALUES ({code_in},{code_ex},{topic_in},{topic_ex},(SELECT id_client FROM `mqttclient` WHERE client = '{id_client_in}'),
        (SELECT id_client FROM `mqttclient` WHERE client = '{id_client_ex}'),{condition},{affiche_list_function(function_)})"""
        mycursor = dbb.cursor()
        mycursor.execute(sql)
        return "Client Mqtt Ajouter"
    except mysql.connector.errors.IntegrityError as e:
        print(f"erreur_{separation_socket}{e}".encode(encode_socket))
        conn.sendall(f"erreur_{separation_socket}{e}".encode(encode_socket))


ThreadMqtt = Thread_custom(target=callback, name="callback")
ThreadMqtt.Daemon = True

if config["start"]:
    is_start = True
    ThreadMqtt.start()
    for (titreTopic) in print_titreTopic():
        client.subscribe(titreTopic, 0)
    look = True
    

# Socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    with multiprocessing.Pool(nb_workers) as pool:
        while True:
            conn, address = s.accept()
            with conn:
                if (
                    white_list_ip_socket.count(
                        str(address[0])
                    )
                    > 0
                ):
                    buff = conn.recv(buff_socket)
                    # message = buff.decode('utf-8')
                    slipte = buff.decode(encode_socket).split(
                        separation_socket
                    )
                    try:
                        action = slipte[0]
                    except IndexError:
                        conn.sendall(f"erreur_{separation_socket}".encode(encode_socket))
                    try:
                        action_1 = slipte[1]
                    except IndexError:
                        conn.sendall(f"erreur_{separation_socket}".encode(encode_socket))
                    
                    if action == "list":
                        if action_1 == "topic":
                            conn.sendall(f"list{separation_socket}{print_titreTopic()}".encode(encode_socket))
                        if action_1 == "client":
                            conn.sendall(f"list{separation_socket}{liste_client()}".encode(encode_socket))
                        if action_1 == "cache":
                            conn.sendall(f"list{separation_socket}{liste_cache()}".encode(encode_socket))
                    if action == "server":
                        if action_1 == "start":
                            is_start = True                            
                            try:
                                if not look:
                                    for titreTopic in print_titreTopic():
                                        client.subscribe(titreTopic, 0)
                                        print(titreTopic)
                                    look = True
                                if not ThreadMqtt.is_alive():
                                    ThreadMqtt.start()
                                conn.sendall(
                                    f"{action}{separation_socket}{action_1}{separation_socket}{is_start}".encode(
                                        encode_socket
                                    )
                                )
                            except RuntimeError as e:
                                conn.sendall(
                                    f"erreur start {e}".encode(
                                        encode_socket
                                    )
                                )
                                print("server start")
                        if action_1 == "stop":
                            is_start = False                 
                            conn.sendall(
                                f"{action}{separation_socket}{action_1}{separation_socket}{is_start}".encode(
                                    encode_socket
                                )
                            )
                            print("server stop")
                            # break
                        if action_1 == "status":
                            conn.sendall(
                                f"{action}{separation_socket}{action_1}{separation_socket}{is_start}".encode(
                                    encode_socket
                                )
                            )
                            print(f"{action}{separation_socket}{action_1}{separation_socket}{is_start}")
                    if action == "objet":
                        if action_1 == "topic":
                            value = slipte[2]
                            liste = cache_topic(value)
                            print(liste)
                            conn.sendall(f"{liste}".encode(encode_socket))
                        if action_1 == "is_co":
                            call_All_Objet()
                            conn.sendall(
                                f"exe".encode(encode_socket)
                            )
                    if action == "add":
                        if action_1 == "client":
                            uid = slipte[2]
                            name = slipte[3]
                            conn.sendall(f"exe;{add_client(mydb,name,uid)}".encode(encode_socket))
                    if action == "update":
                        if action_1 == "client":
                            uid = slipte[2]
                            name = slipte[3]
                            conn.sendall(f"exe;{update_client(mydb,name,uid)}".encode(encode_socket))
                            
