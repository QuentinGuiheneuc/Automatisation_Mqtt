# Automatisation_Mqtt

## Instal

```
apt-get install mosquitto
pip3 install paho-mqtt
```

Avant de démarrer le multiservise il faut editer le fichier config.json.
Il y a 4 fichier sql, il faudra a jouter a votre basse de donnée.
Dans un fichier config.json, il faut ajouter dans le dossier la config dans votre projet.

```
"socket": {
    "host": "192.168.1.39",
    "port": 65000,
    "buff": 2000,
    "separation": ";"
  }
```
