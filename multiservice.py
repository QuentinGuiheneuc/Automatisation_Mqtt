from threading import Thread
import paho.mqtt.client as mqtt
import time, threading
import mysql.connector
import json
import socket,multiprocessing
import os

def lire_fichier_Json(fichier):
    with open(fichier) as fichiers:
        return json.load(fichiers)

config = lire_fichier_Json("config.json")
client = mqtt.Client(config["mqtt"]["clientId"],userdata=True)
client.username_pw_set(config["mqtt"]["username"], config["mqtt"]["password"])
client.connect(config["mqtt"]["serverUrl"],config["mqtt"]["port"])
separation = config["mqtt"]["separation"]
host = config["socket"]["host"] 
port = config["socket"]["port"]
nb_workers = config["socket"]["nb_workers"]
is_start = False
buff_socket = config["socket"]["buff"]
separation_socket = config["socket"]["separation"]
white_list_ip_socket = config["socket"]["white_list_ip"]
user_socket = ""

mydb = mysql.connector.connect(
    host=config["mysql"]["host"],
    port= config["mysql"]["port"],
    user=config["mysql"]["user"],
    password=config["mysql"]["password"],
    database=config["mysql"]["database"]
)

def error():
    return lire_fichier_Json("erreur.json")

def list_error(code_in):
    list = []
    for code in error():
        list.append(code)
    return list.count(code_in)

def print_titreTopic():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT topic FROM `mqtttopic`")
    myresult = mycursor.fetchall()
    text = []
    for topic in myresult:
        for item in topic:
            text.append(item)
    return text

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

def cache_(bbd,message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    pay = payload.split(";")
    name_client = pay[1]
    mycursor = bbd.cursor()  
    mycursor.execute(f"SELECT id_client FROM `mqttcache` WHERE `id_client` = (SELECT id_client FROM `mqttclient` WHERE client = '{name_client}' ) ")
    myresult = mycursor.fetchall()
    print(myresult)
    if myresult != []:
        sql = f"UPDATE `mqttcache` SET `ressult`='{payload}' WHERE (SELECT id_client FROM `mqttclient` WHERE client = '{name_client}')"
        mycursor.execute(sql)
        bbd.commit()
    else:
        sql = f"INSERT INTO `mqttcache`(`id_topic`, `id_client`, `ressult`) VALUES ((SELECT id_topic FROM `mqtttopic` WHERE topic = '{topic}'),(SELECT id_client FROM `mqttclient` WHERE client = '{name_client}'), '{payload}')"
        mycursor.execute(sql)
        bbd.commit()

def add_client(bbd, uid):
    mycursor = bbd.cursor()
    mycursor.execute("SELECT client,uid FROM `mqttclient` WHERE `uid` = "+ uid)
    myresult = mycursor.fetchall()
    print(myresult)
    if myresult == []:
        client = random.randrange(1000000000,9999999999)
        sql = "INSERT INTO mqttclient (client, uid) VALUES (%s, %s)"
        val = (client, uid)
        mycursor.execute(sql, val)
        bbd.commit()
        print("Inserted")
        mycursor.execute("SELECT client,uid FROM `mqttclient` WHERE `uid` = "+ uid)
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
                    val = (titre, text, key["types"],"icons/{0}".format(key["icon"]),dateNow,key["color"])     
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
    mycursor.execute("SELECT client,uid FROM `mqttclient` WHERE `uid` = "+ uid)
    myresult = mycursor.fetchall()
    print(myresult)
    if myresult != []:
        sql = "UPDATE `mqttclient` SET is_alive = %s WHERE uid = %s"
        val = (1, uid)
        mycursor.execute(sql, val)
        bbd.commit()

def execute(bbd,message,mqtt,separation):

        topic = message.topic
        payload = message.payload.decode("utf-8")
        pay = payload.split(";")
        codeIn = pay[0]
        print("execute",codeIn, not list_error(pay[0]))
        if not list_error(pay[0]):
            clientIn = pay[1]
            rek = """
            SELECT mqc_e.client,mqc.client,mqe.code_ex,mqe.topic_ex,mqe.condition FROM `mqttexecut` as mqe 
            INNER JOIN `mqttclient` as mqc ON mqe.client_id_in = mqc.id_client
            INNER JOIN `mqttclient` as mqc_e ON mqe.client_id_ex = mqc_e.id_client 
            WHERE mqe.code_in = '{0}' and mqe.topic_in = '{1}' and mqc.client = '{2}'""".format(codeIn,topic,clientIn)
            print(rek)
            mycursor = bbd.cursor()  
            mycursor.execute(rek) 
            myresult = mycursor.fetchall()
            print(myresult)
            if myresult != []:
                for result in myresult:
                    client_ex = result[0]
                    client_in = result[1]
                    code_ex  = result[2]
                    topic_ex = result[3]
                    if result[4] != "":
                        # print(result[4])
                        conditionJsonBdd = json.loads(result[4])
                        if len(pay) > 2:
                            print(pay[2])
                            conditionJsonIn = json.loads(pay[2])
                        for keyobj,valueobj in conditionJsonIn.items():
                            for keybdd,valuebdd in conditionJsonBdd.items():
                                if keyobj == keybdd:
                                    exe = executeConsition(int(valueobj),valuebdd['condition'],int(valuebdd['value']))
                                    dis = {keyobj:exe}
                                    message = f'{code_ex}{separation}{client_ex}{separation}{json.dumps(dis)}'
                                    print("message",message)
                                    mqtt.publish(client_ex,message,0)
            
def executeConsition(value_1 , condition, value_2):
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
        database=config["mysql"]["database"]
    )

    payload = message.payload.decode("utf-8")
    print(" < received message " + payload + " " + message.topic)
    notify_error(mydb1,message)
    if payload.startswith("400"): # demanded on client
        pay = payload.split(separation)
        CLient = add_client(mydb1,pay[1])
        client.publish(pay[2],f"401{separation}{CLient}", 1)
        CLient = ""
    if payload.startswith("404"):
        print(listeObjet(mydb1,message))
    if payload.startswith("405"):
        call_All_Objet();
    execute(mydb1,message,client,separation)
    cache_(mydb1,message)
    mydb1.close()
def on_publish(client, userdata, mid):
    print(" > published message: {}".format(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection.{str(userdata)}")

def mqttsub(topic):
    client.on_message = on_execut
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.loop_start()
    client.subscribe(topic,0)

def call_All_Objet():
    initListeObjet(mydb)
    client.publish("listeObjet" , "403")

def liste_client():
    rek = "SELECT client FROM `mqttclient`"
    mycursor = mydb.cursor()  
    mycursor.execute(rek) 
    myresult = mycursor.fetchall()
    print(myresult)
    return myresult

def liste_cache():
    rek = "SELECT `id_topic`, `id_client`, `ressult` FROM `mqttcache`"
    mycursor = mydb.cursor()  
    mycursor.execute(rek) 
    myresult = mycursor.fetchall()
    print(myresult)
    return myresult

def cache_topic(topic):
    mydb = mysql.connector.connect(
        host=config["mysql"]["host"],
        port= config["mysql"]["port"],
        user=config["mysql"]["user"],
        password=config["mysql"]["password"],
        database=config["mysql"]["database"]
    )
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT (SELECT client FROM `mqttclient` WHERE id_client =  mqca.id_client ) ,  mqca.ressult FROM mqttcache as mqca WHERE mqca.id_topic = (SELECT `id_topic` FROM `mqtttopic` WHERE `topic` = '{topic}')")
    myresult = mycursor.fetchall()
    dis = {}
    i = 0
    for topic in myresult:
        resulta_ = topic[1].split(separation)
        dis_1 = {
            "client": topic[0], 
            "topic": resulta_[0], 
            "value": json.loads(resulta_[2])
            }
        dis[str(i)] = dis_1
        i+=1
    # print(json.dumps(dis))
    mydb.close()
    return json.dumps(dis)
# Socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    with multiprocessing.Pool(nb_workers) as pool:
        while True:
            conn, address = s.accept()
            with conn:
                if white_list_ip_socket.count(str(address[0])) > 0 :
                    buff = conn.recv(buff_socket)
                    # message = buff.decode('utf-8')
                    slipte = buff.decode('utf-8').split(separation_socket)
                    action = slipte[0]
                    action_1 = slipte[1]
                    if action == "list":
                        if action_1 == "topic":
                            conn.sendall(f"liste{separation_socket}{print_titreTopic()}".encode('utf-8'))
                        if action_1 == "client":
                           conn.sendall(f"liste{separation_socket}{liste_client()}".encode("utf-8"))
                        if action_1 == "cache":
                            conn.sendall(f"liste{separation_socket}{liste_cache()}".encode("utf-8"))
                    if action == "server":    
                        if action_1 == "start":
                            for titreTopic in print_titreTopic():
                                mqttsub(titreTopic)
                            is_start = True
                            conn.sendall(f"{action}{separation_socket}{action_1}{separation_socket}{is_start}".encode('utf-8'))
                        if action_1 == "stop":
                            for titreTopic in print_titreTopic():
                                client.unsubscribe(titreTopic)
                            is_start = False
                            conn.sendall(f"{action}{separation_socket}{action_1}{separation_socket}{is_start}".encode('utf-8'))
                            conn.close()
                            # break
                        if action_1 == "status":
                            conn.sendall(f"{action}{separation_socket}{action_1}{separation_socket}{is_start}".encode('utf-8'))
                    if action == "objet":
                        if action_1 == "topic":
                            value = slipte[2]
                            print(cache_topic(value))
                            conn.sendall(f"{cache_topic(value)}".encode("utf-8"))
                        