#!/bin/bash

LOG_PATH=""
if [ $1 == "production" ]; then
    LOG_PATH="/var/log/smartvending/server/production.log"
elif [ $1 == "rabbit-consumer" ]; then
    LOG_PATH="/var/log/smartvending/server/rabbitmq-consumer.log"
elif [ $1 == "veritrans" ]; then
    LOG_PATH="/var/log/smartvending/server/veritrans.log"
elif [ $1 == "ui" ]; then
    LOG_PATH="/var/log/smartvending/server/ui.log"    
elif [ $1 == "controller" ]; then
    LOG_PATH="/var/log/smartvending/controller/indoshakecontroller.log"
elif [ $1 == "virtual-tty" ]; then
    if [[ -z "${VIRTUAL_TTY_LOG_PATH}" ]]; then
      LOG_PATH="${VIRTUAL_TTY_LOG_PATH}"
    else
      echo "Unable to find path for virtual-tty.log file"
      exit
    fi    
elif [ $1 == "svm-scheduled-restart" ]; then
    LOG_PATH="/var/log/smartvending/system/svm-scheduled-restart.log"
fi

if [ ! -z "${LOG_PATH}" ]; then
    tail -F "$LOG_PATH"
else
    echo "Wrong argument"
fi
