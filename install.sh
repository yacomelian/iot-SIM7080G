#!/bin/bash

./scripts/initialize_gpio.sh

apt install git python3 python3-pip
apt install git python3-rpi.gpio python3-serial python3-yaml
pip3 install -r requirements.txt


