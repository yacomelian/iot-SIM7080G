#!/bin/bash

echo "4" > /sys/class/gpio/export
sleep 0.1
echo "out" > /sys/class/gpio/gpio4/direction
echo "0" > /sys/class/gpio/gpio4/value