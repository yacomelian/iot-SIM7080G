#!/bin/bash


[ "$UID" -eq 0 ] || exec sudo "$0" "$@"

echo 'Ejecutar como root'
# Ubuntu 20.04
if [[  $(grep 20.04 /etc/os-release  | grep -ci ubuntu) -ge "1"  ]]; then
    echo "Ubuntu"
    #echo ACTION=="add", KERNEL=="ttyS0", MODE="0666"
    # Buscar otra solucion, mientras
    #chmod 0666 /dev/ttyS*
    #chmod 0666 /dev/ttyUSB*
    if  [[ ! -f "/etc/udev/rules.d/99-local-tty.sh" ]]; then
        echo 'SUBSYSTEM="tty", GROUP="dialout"' > /etc/udev/rules.d/99-local-tty.sh
        #echo 'KERNEL=="ttyS[0-9]+", NAME="tts/%n", SYMLINK+="%k", GROUP="dialout", MODE="0660"' >> /etc/udev/rules.d/99-local-tty.sh
        #echo 'KERNEL=="ttyS0, NAME="tts/%n", SYMLINK+="%k", GROUP="dialout", MODE="0660"' >> /etc/udev/rules.d/99-local-tty.sh
        #sudo echo 'KERNEL=="ttyUSB[0-9]*", NAME="tts/%n", SYMLINK+="%k", GROUP="dialout"Ñ, MODE="0660"' >> /etc/udev/rules.d/99-local-tty.sh
        #KERNEL=="ttyS0", SYMLINK+="serial0" GROUP="tty" MODE="0660"
        #KERNEL=="ttyAMA0", SYMLINK+="serial1" GROUP="tty" MODE="0660"
        #echo 'SUBSYSTEM="tty", GROUP="dialout"' > /etc/udev/rules.d/99-local-tty.sh
        # Visto en foros
        # sudo systemctl stop serial-getty@ttyAMA0.service
        # sudo systemctl disable serial-getty@ttyAMA0.service
        # sudo gpasswd --add pi dialout
        udevadm control --reload-rules && udevadm trigger
    fi

    if  [[ $(grep -c 'enable_uart=1' /boot/firmware/cmdline.txt  ) -le "0" ]]; then
        #enable_uart=1 >> /boot/firmware/cmdline.txt
        # /boot/firmware/cmdline.txt
        # ORIGINAL echo 'net.ifnames=0 dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=LABEL=writable rootfstype=ext4 elevator=deadline rootwait fixrtc' > /boot/firmware/cmdline.txt
        cmdline=$(cat /boot/firmware/cmdline.txt )
        echo $cmdline | sed 's/console=serial0,115200//' > /boot/firmware/cmdline.txt
        #echo 'net.ifnames=0 dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=LABEL=writable rootfstype=ext4 elevator=deadline rootwait fixrtc' > /boot/firmware/cmdline.txt
        systemctl stop serial-getty@ttyS0.service && systemctl disable serial-getty@ttyS0.service
    fi
fi

echo "Otro"
if [[ -f ./scripts/initialize_gpio.sh ]]; then
    ./scripts/initialize_gpio.sh
fi

apt install -y git python3 python3-pip python3-rpi.gpio python3-serial python3-yaml python3-numpy

# Esto sería para ejecutar por el usuario:
# pip3 install -r requirements.txt