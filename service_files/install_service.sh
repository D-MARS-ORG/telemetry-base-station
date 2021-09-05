#!/bin/bash

sudo systemctl stop mqtt_broker.service
sudo systemctl stop mqtt_to_firebase.service

sudo mkdir /opt/dmars
sudo cp -r ../src/* /opt/dmars/
chmod +x /opt/dmars/*.py

sudo cp ./mqtt_broker.service /lib/systemd/system/
sudo cp ./mqtt_to_firebase.service /lib/systemd/system/

sudo chmod 644 /lib/systemd/system/mqtt_broker.service
sudo chmod 644 /lib/systemd/system/mqtt_to_firebase.service

sudo systemctl daemon-reload
sudo systemctl enable mqtt_broker.service
sudo systemctl start mqtt_broker.service

sudo systemctl enable mqtt_to_firebase.service
sudo systemctl start mqtt_to_firebase.service

