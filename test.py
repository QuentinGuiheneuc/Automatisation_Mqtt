import socket

host = "192.168.1.39"
port = 65000



def sock_envoie(sock):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(sock.encode('utf-8'))
    buff = s.recv(512)
    print(buff.decode())

while True:
    for i in range(1):
        print("_________________________________________")
        print("| Strat Server --> s                     |")
        print("| Stop Server --> sp                     |")
        print("| Status Server --> st                   |")
        print("| Select all topic prise --> topic       |")
        print("| exit progarme --> exit                 |")
        print("__________________________________________")
    mode= str(input("mode:"))
    if mode == "s":
      sock_envoie("server;start")
    elif mode == "sp":
      sock_envoie("server;stop")
    elif mode == "st":
          sock_envoie("server;status")
    elif mode == "topic":
          sock_envoie("objet;topic;prise")
    elif mode=="exit": # Quit
        break