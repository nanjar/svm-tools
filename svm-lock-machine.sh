#!/bin/bash

SVM_LOCK_STATE_FILE="/boot/machine.lock"

clear_screen() {
    sudo pkill -f "svm-show-image.py"
}

create_state_file() {
    if [ ! -f "$SVM_LOCK_STATE_FILE" ]; then
        sudo unlock-system boot
        sudo touch "$SVM_LOCK_STATE_FILE"
        sudo lock-system
    fi
}

remove_state_file() {
    if [ -f "$SVM_LOCK_STATE_FILE" ]; then
        sudo unlock-system boot
        sudo rm -f "$SVM_LOCK_STATE_FILE"
        sudo lock-system
    fi
}

ASSET_DIR="asset-svm-lock-machine"
ENV_NAME="$ASSET_DIR"/"env"
CALLER_DIR="$PWD"
PY_BASE_DIR=$(readlink -f $0 | xargs dirname)/py
ENV_DIR="$PY_BASE_DIR/$ENV_NAME"

if [ ! -d "$ENV_DIR" ]; then
    sudo unlock-system
    echo "Creating env only for the first time..."
    sudo python3 -m venv $ENV_DIR
    sudo chown -R pi.pi $ENV_DIR
    sudo chown -R pi.pi /opt/svm-tools/img/svm-machine-under-maintenance.png
    source $ENV_DIR/bin/activate
    echo "Installing necessary packages..."
    cd $PY_BASE_DIR
    pip3 install -r "$ASSET_DIR"/requirements.txt
    deactivate
    sudo lock-system
    cd $CALLER_DIR
    echo "Packages installation is done."
    echo ""
fi

deactivate > /dev/null 2>&1
source $ENV_DIR/bin/activate

if [ $# -eq 0 ]; then
    clear_screen
    python3 /opt/svm-tools/py/svm-show-image.py --file /opt/svm-tools/img/svm-machine-under-maintenance.png --display :0.0 --persistence &
    create_state_file
    sudo systemctl stop pyshake.service
    pm2 stop all
elif [ $1 == "--reload" ]; then
    if [ -f "$SVM_LOCK_STATE_FILE" ]; then
        python3 /opt/svm-tools/py/svm-show-image.py --file /opt/svm-tools/img/svm-machine-under-maintenance.png --display :0.0 --persistence &
        pm2 stop all
        sudo systemctl stop pyshake.service
    fi
elif [ $1 == "--unlock" ]; then
    sudo systemctl restart pyshake.service
    pm2 reload all
    remove_state_file
    clear_screen
else
    echo "========================================="
    echo "Lock machine and showing under maintenance display"
    echo ""
    echo "Usage: "
    echo "$0                  Lock machine and show machine under maintenance on screen"
    echo "$0 --unlock         Unlock machine"
    echo "$0 --reload         Reload lock machine screen if the machine is already locked"
    echo "$0 --help           Show this help page"
fi
