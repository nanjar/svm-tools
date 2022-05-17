#!/bin/bash

CALIBRATION_CONFIG_FILE="/usr/share/X11/xorg.conf.d/99-tscalibration.conf"
CALIBRATION_TMP_FILE="/tmp/99-tscalibration.conf"

if [ -f "$CALIBRATION_TMP_FILE" ]; then
    rm "$CALIBRATION_TMP_FILE"
fi

DISPLAY=:0.0 xinput_calibrator --output-filename "$CALIBRATION_TMP_FILE"

# If calibration is success, the temporary conf file will be created
if [ -f "$CALIBRATION_TMP_FILE" ]; then
    pm2 stop all
    sudo unlock-system -p
    sudo mv -f "$CALIBRATION_TMP_FILE" "$CALIBRATION_CONFIG_FILE" && sync
    sudo lock-system
    pm2 reload all
fi
