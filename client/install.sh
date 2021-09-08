#! /bin/bash
# install system 
cp mqtt_client.service /etc/systemd/system
systemctl enable mqtt_client.service
