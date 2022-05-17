#!/bin/bash
INIT_MACHINE_STATE_FILE="/boot/state.svm"

check_bootloader_config() {
    echo "Checking bootloader config..."
    echo $(vcgencmd bootloader_config)
    BOOT_ORDER=$(vcgencmd bootloader_config | grep BOOT_ORDER=0xf14)
    if [ ! "$BOOT_ORDER" = "BOOT_ORDER=0xf14" ]; then
        sudo unlock-system boot
        sudo cp -f /opt/svm-tools/boot-recovery/pieeprom.sig /boot/
        sudo cp -f /opt/svm-tools/boot-recovery/pieeprom.upd /boot/
        sudo cp -f /opt/svm-tools/boot-recovery/recovery.bin /boot/
        sync
        sudo lock-system
        sudo reboot now
    fi
}

cleanup_bootloader_recovery() {
    echo "Cleanup bootloader recovery..."
    if [ -f "/boot/pieeprom.sig" ]; then
        sudo unlock-system boot
        sudo rm -f /boot/pieeprom.sig
        sync
        sudo lock-system
    fi
    
    if [ -f "/boot/pieeprom.upd" ]; then
        sudo unlock-system boot
        sudo rm -f /boot/pieeprom.upd
        sync
        sudo lock-system
    fi
    
    if [ -f "/boot/recovery.bin" ]; then
        sudo unlock-system boot
        sudo rm -f /boot/recovery.bin
        sync
        sudo lock-system
    fi
    
    if [ -f "/boot/RECOVERY.000" ]; then
        sudo unlock-system boot
        sudo rm -f /boot/RECOVERY.000
        sync
        sudo lock-system
    fi    
}

enable_all_services() {
    echo "Enable all services..."
    sudo unlock-system -p
    sudo systemctl enable mysql.service
    sudo systemctl enable mariadb.service
    sudo systemctl enable mysqld.service
    sudo systemctl enable nginx.service
    sudo systemctl enable rabbitmq-server.service
    sudo systemctl enable rabbit-consumer.service
    sudo systemctl enable virtual-tty-relay.service
    sudo systemctl enable pyshake.service
    sudo systemctl enable pm2-pi.service
    sudo lock-system
}

start_all_services() {
    echo "Start all services..."
    sudo systemctl start mysql.service
    sudo systemctl start mariadb.service
    sudo systemctl start mysqld.service
    sudo systemctl start nginx.service
    sudo systemctl start rabbitmq-server.service
    sudo systemctl stop pyshake.service
    sudo systemctl stop pm2-pi.service
}

cleanup_init_machine_flag() {
    echo "Cleanup init machine flag..."
    sudo unlock-system boot
    sudo rm -f "$INIT_MACHINE_STATE_FILE"
    sync
    sudo lock-system
}

wait_xserver() {
    # Wait until X is ready
    while [ ! -f "/run/X-ready.tmp" ]
    do
        sleep 1
    done
}

if [ -f "$INIT_MACHINE_STATE_FILE" ]; then
    STATE_SVM=$(<"$INIT_MACHINE_STATE_FILE")
    if [ "$STATE_SVM" = "config id" ]; then
        sudo systemctl stop pm2-pi.service
    
        check_bootloader_config
        cleanup_bootloader_recovery

        wait_xserver
        
        echo "Entering jail before setting config..."
        source /opt/svm-tools/py/asset-svm-set-machine-config/env/bin/activate
        export DISPLAY=:0
        sudo -u pi python3 /opt/svm-tools/py/svm-set-machine-config.py

    elif [ "$STATE_SVM" = "init id" ]; then
        sudo systemctl stop pm2-pi.service
        
        cleanup_bootloader_recovery
        wait_xserver
        
        echo "Entering jail before init..."
        source /opt/svm-tools/py/asset-svm-init-machine/env/bin/activate
        export DISPLAY=:0
        sudo -u pi python3 /opt/svm-tools/py/svm-init-machine.py
        cleanup_init_machine_flag
    fi
fi

