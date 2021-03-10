#!/bin/bash

echo 'Ejecutar como root'
[ "$UID" -eq 0 ] || exec sudo "$0" "$@"


rm /etc/udev/rules.d/99-local-tty.sh
