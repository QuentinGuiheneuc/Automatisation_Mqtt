<?php
class treert {

    public function MQTT_multiservice($in,$json=true) {
        $configJson = json_decode(file_get_contents("config/config.json"),true);
        error_reporting(E_ALL);
        /*Lit le port*/
        $service_port = $configJson["socket"]["port"];
        /*Lit l'adresse IP du serveur de destination*/
        $address = $configJson["socket"]["host"];
        /* Crée un socket TCP/IP. */
        $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        $result = socket_connect($socket, $address, $service_port);
        $out = '';
        socket_write($socket, $in, strlen($in));
        while ($out = socket_read($socket, $configJson["socket"]["buff"])) {
            if ($configJson["socket"]["separation"] != "" && $json){
                return explode($configJson["socket"]["separation"],$out);
            }else{
                return $out;
            }
        }
        return $out;
    }
    public function start(){
        $resul = $this->MQTT_multiservice("server;start");
        $resul[3];
    }
    public function stop(){
        $resul = $this->MQTT_multiservice("server;stop");
        $resul[3];
    }
    public function liste_topic($topic){
        $resul = $this->MQTT_multiservice("objet;topic;".$topic, false);
        var_dump($resul);
        return json_decode($resul,true);
    }

}

?>